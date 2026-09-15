# [H] CVE-2017-9984

## Summary
Severity: High
Advisory: CVE-2017-9984
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9984
Type: osv

## Details
The snd_msnd_interrupt function in sound/isa/msnd/msnd_pinnacle.c in the Linux kernel through 4.11.7 allows local users to cause a denial of service (over-boundary access) or possibly have unspecified other impact by changing the value of a message queue head pointer between two kernel reads of that value, aka a "double fetch" vulnerability.

## References
- http://www.securityfocus.com/bid/99314
- https://github.com/torvalds/linux/commit/20e2b791796bd68816fa115f12be5320de2b8021
- https://usn.ubuntu.com/3754-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=20e2b791796bd68816fa115f12be5320de2b8021
- https://bugzilla.kernel.org/show_bug.cgi?id=196131
