# [H] CVE-2017-18270

## Summary
Severity: High
Advisory: CVE-2017-18270
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2017-18270
Type: osv

## Details
In the Linux kernel before 4.13.5, a local user could create keyrings for other users via keyctl commands, setting unwanted defaults or causing a denial of service.

## References
- https://support.f5.com/csp/article/K37301725
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/104254
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.5
- https://bugzilla.redhat.com/show_bug.cgi?id=1580979
- https://bugzilla.redhat.com/show_bug.cgi?id=1856774#c11
- https://bugzilla.redhat.com/show_bug.cgi?id=1856774#c9
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=237bbd29f7a049d310d907f4b2716a7feef9abf3
- https://github.com/torvalds/linux/commit/237bbd29f7a049d310d907f4b2716a7feef9abf3
