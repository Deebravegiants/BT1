# [H] CVE-2016-7425

## Summary
Severity: High
Advisory: CVE-2016-7425
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2016-7425
Type: osv

## Details
The arcmsr_iop_message_xfer function in drivers/scsi/arcmsr/arcmsr_hba.c in the Linux kernel through 4.8.2 does not restrict a certain length field, which allows local users to gain privileges or cause a denial of service (heap-based buffer overflow) via an ARCMSR_MESSAGE_WRITE_WQBUFFER control code.

## References
- http://www.securityfocus.com/bid/93037
- https://security-tracker.debian.org/tracker/CVE-2016-7425
- http://www.ubuntu.com/usn/USN-3144-2
- http://www.ubuntu.com/usn/USN-3146-1
- http://www.ubuntu.com/usn/USN-3145-2
- http://www.ubuntu.com/usn/USN-3146-2
- http://www.openwall.com/lists/oss-security/2016/09/17/2
- http://www.ubuntu.com/usn/USN-3144-1
- http://www.ubuntu.com/usn/USN-3145-1
- http://www.ubuntu.com/usn/USN-3147-1
- http://marc.info/?l=linux-scsi&m=147394796228991&w=2
- https://bugzilla.redhat.com/show_bug.cgi?id=1377330
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7bc2b55a5c030685b399bb65b6baa9ccc3d1f167
- https://github.com/torvalds/linux/commit/7bc2b55a5c030685b399bb65b6baa9ccc3d1f167
- http://marc.info/?l=linux-scsi&m=147394713328707&w=2
