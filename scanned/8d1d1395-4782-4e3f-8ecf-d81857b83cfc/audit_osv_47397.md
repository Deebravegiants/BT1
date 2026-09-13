# [H] CVE-2016-4558

## Summary
Severity: High
Advisory: CVE-2016-4558
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4558
Type: osv

## Details
The BPF subsystem in the Linux kernel before 4.5.5 mishandles reference counts, which allows local users to cause a denial of service (use-after-free) or possibly have unspecified other impact via a crafted application on (1) a system with more than 32 Gb of memory, related to the program reference count or (2) a 1 Tb system, related to the map reference count.

## References
- https://github.com/torvalds/linux/commit/92117d8443bc5afacc8d5ba82e541946310f106e
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=92117d8443bc5afacc8d5ba82e541946310f106e
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.5
- http://www.openwall.com/lists/oss-security/2016/05/06/4
- http://www.ubuntu.com/usn/USN-3005-1
- http://www.ubuntu.com/usn/USN-3006-1
- http://www.ubuntu.com/usn/USN-3007-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1334303
