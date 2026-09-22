# [H] CVE-2018-16880

## Summary
Severity: High
Advisory: CVE-2018-16880
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2018-16880
Type: osv

## Details
A flaw was found in the Linux kernel's handle_rx() function in the [vhost_net] driver. A malicious virtual guest, under specific conditions, can trigger an out-of-bounds write in a kmalloc-8 slab on a virtual host which may lead to a kernel memory corruption and a system panic. Due to the nature of the flaw, privilege escalation cannot be fully ruled out. Versions from v4.16 and newer are vulnerable.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00037.html
- http://www.securityfocus.com/bid/106735
- https://support.f5.com/csp/article/K03593314
- https://usn.ubuntu.com/3903-1/
- https://usn.ubuntu.com/3903-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16880
