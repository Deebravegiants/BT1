# [M] CVE-2018-6459

## Summary
Severity: Medium
Advisory: CVE-2018-6459
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-02-20
Source: https://osv.dev/vulnerability/CVE-2018-6459
Type: osv

## Details
The rsa_pss_params_parse function in libstrongswan/credentials/keys/signature_params.c in strongSwan 5.6.1 allows remote attackers to cause a denial of service via a crafted RSASSA-PSS signature that lacks a mask generation function parameter.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00047.html
- https://security.gentoo.org/glsa/201811-16
- https://www.strongswan.org/blog/2018/02/19/strongswan-vulnerability-%28cve-2018-6459%29.html
