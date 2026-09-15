# [H] CVE-2016-3070

## Summary
Severity: High
Advisory: CVE-2016-3070
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-3070
Type: osv

## Details
The trace_writeback_dirty_page implementation in include/trace/events/writeback.h in the Linux kernel before 4.4 improperly interacts with mm/migrate.c, which allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact by triggering a certain page move.

## References
- http://www.securityfocus.com/bid/90518
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://www.ubuntu.com/usn/USN-3034-2
- http://www.ubuntu.com/usn/USN-3036-1
- http://www.ubuntu.com/usn/USN-3037-1
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.ubuntu.com/usn/USN-3034-1
- http://www.ubuntu.com/usn/USN-3035-1
- http://www.ubuntu.com/usn/USN-3035-2
- http://www.ubuntu.com/usn/USN-3035-3
- https://security-tracker.debian.org/tracker/CVE-2016-3070
- http://www.debian.org/security/2016/dsa-3607
- https://bugzilla.redhat.com/show_bug.cgi?id=1308846
- https://github.com/torvalds/linux/commit/42cb14b110a5698ccf26ce59c4441722605a3743
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=42cb14b110a5698ccf26ce59c4441722605a3743
