# [M] CVE-2016-8635

## Summary
Severity: Medium
Advisory: CVE-2016-8635
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-8635
Type: osv

## Details
It was found that Diffie Hellman Client key exchange handling in NSS 3.21.x was vulnerable to small subgroup confinement attack. An attacker could use this flaw to recover private keys by confining the client DH key to small subgroup of the desired group.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2779.html
- http://www.securityfocus.com/bid/94346
- https://security.gentoo.org/glsa/201701-46
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8635
