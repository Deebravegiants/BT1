# [H] CVE-2017-15135

## Summary
Severity: High
Advisory: CVE-2017-15135
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2017-15135
Type: osv

## Details
It was found that 389-ds-base since 1.3.6.1 up to and including 1.4.0.3 did not always handle internal hash comparison operations correctly during the authentication process. A remote, unauthenticated attacker could potentially use this flaw to bypass the authentication process under very rare and specific circumstances.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00033.html
- http://www.securityfocus.com/bid/102811
- https://access.redhat.com/errata/RHSA-2018:0414
- https://access.redhat.com/errata/RHSA-2018:0515
- https://bugzilla.redhat.com/show_bug.cgi?id=1525628
