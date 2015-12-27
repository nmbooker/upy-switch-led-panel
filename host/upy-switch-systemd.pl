#!/usr/bin/perl

# sudo apt-get install libio-async-perl libgetopt-long-perl

use v5.10;

use IO::Async::Loop;
use IO::Async::Stream;
use IO::Async::Timer::Periodic;

use autodie qw/:io/;

use Getopt::Long qw/:config gnu_getopt/;

my $jobtabfile = '/usr/local/etc/upy-switch-systemd/jobtab';

GetOptions('jobtab=s' => \$jobtabfile);

my @jobtab = do {
    my @t;
    open(my $file, '<', $jobtabfile);
    foreach (<$file>) {
	chomp;
	s/#.*$//;      # Strip out comments
	next if /^\s*$/;    # Ignore lines that are all whitespace
	if (/^\s*([a-zA-Z0-9]+)\s+([a-zA-Z0-9]+)\s+([a-zA-Z0-9]+)\s*$/) {
	    push @t, {
		job => $1,
		switch => $2,
		led => $3,
            };
	}
    }
    @t;
};

my $loop = IO::Async::Loop->new;

open(my $ser, '+<', '/dev/ttyACM0');

my $ser_stream = IO::Async::Stream->new(
    handle => $ser,
    on_read => \&on_read_line,
    );


my %jobled = map { $_->{job} => $_->{led} } @jobtab;
my %switchjob = map { $_->{switch} => $_->{job} } @jobtab;

my $poller = IO::Async::Timer::Periodic->new(
    interval => 1,
    on_tick => sub {
	for my $job (keys %jobled) {
	    my $led = $jobled{$job};
	    my $cmd = sprintf("LED %s %s", $led,
			      (is_running($job) ? 'ON' : 'OFF'));
	    $ser->write("\r\n$cmd\r\n");
	}
    },
    );

$poller->start;

$loop->add($ser_stream);
$loop->add($poller);

sub is_running {
    my $job = shift;
    my $out = `systemctl status $job.service`;
    $out =~ /Active: activating/;
}

$ser->write("\r\nHELLO\r\n");

$loop->run;

sub on_read_line {
    my $self = shift;
    my ( $buffref, $eof ) = @_;

    while( $$buffref =~ s/^(.*\n)// ) {
	process_line($1);
    }
    
    return 0;
}

sub process_line {
    my ($line) = @_;
    if ($line =~ /^PRESSED ([a-zA-Z0-9]+)/) {
	if (my $job = $switchjob{$1}) {
	    system qw/systemctl start --no-block/, "$job.service";
	}
    }
}
