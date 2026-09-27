# [M] CVE-2010-5321

## Summary
Severity: Medium
Advisory: CVE-2010-5321
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-24
Source: https://osv.dev/vulnerability/CVE-2010-5321
Type: osv

## Details
Memory leak in drivers/media/video/videobuf-core.c in the videobuf subsystem in the Linux kernel 2.6.x through 4.x allows local users to cause a denial of service (memory consumption) by leveraging /dev/video access for a series of mmap calls that require new allocations, a different vulnerability than CVE-2007-6761.  NOTE: as of 2016-06-18, this affects only 11 drivers that have not been updated to use videobuf2 instead of videobuf.

## References
- http://www.openwall.com/lists/oss-security/2015/02/08/4
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=827340
- https://bugzilla.kernel.org/show_bug.cgi?id=120571
- https://bugzilla.redhat.com/show_bug.cgi?id=620629
- http://www.openwall.com/lists/oss-security/2015/02/08/4
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=827340
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=827340
- https://bugzilla.kernel.org/show_bug.cgi?id=120571
- https://bugzilla.redhat.com/show_bug.cgi?id=620629
- http://linuxtv.org/irc/v4l/index.php?date=2010-07-29
