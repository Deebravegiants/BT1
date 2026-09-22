# [H] CVE-2019-3896

## Summary
Severity: High
Advisory: CVE-2019-3896
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-3896
Type: osv

## Details
A double-free can happen in idr_remove_all() in lib/idr.c in the Linux kernel 2.6 branch. An unprivileged local attacker can use this flaw for a privilege escalation or for a system crash and a denial of service (DoS).

## References
- https://support.f5.com/csp/article/K04327111
- http://www.securityfocus.com/bid/108814
- https://security.netapp.com/advisory/ntap-20190710-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3896
