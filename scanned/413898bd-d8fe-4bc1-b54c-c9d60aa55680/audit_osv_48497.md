# [H] CVE-2017-8386

## Summary
Severity: High
Advisory: CVE-2017-8386
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-01
Source: https://osv.dev/vulnerability/CVE-2017-8386
Type: osv

## Details
git-shell in git before 2.4.12, 2.5.x before 2.5.6, 2.6.x before 2.6.7, 2.7.x before 2.7.5, 2.8.x before 2.8.5, 2.9.x before 2.9.4, 2.10.x before 2.10.3, 2.11.x before 2.11.2, and 2.12.x before 2.12.3 might allow remote authenticated users to gain privileges via a repository name that starts with a - (dash) character.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DPYRN7APMHY4ZFDPAKD22J5R4QJFY2JP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FDS3LSJJ3YGGQYIVPKQDVOCXWDSF6JGF/
- http://public-inbox.org/git/xmqq8tm5ziat.fsf%40gitster.mtv.corp.google.com/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3ISHYFLM2ACYHHY3JHCLF75X7UF4ZMDM/
- http://lists.opensuse.org/opensuse-updates/2017-05/msg00090.html
- http://www.securitytracker.com/id/1038479
- https://access.redhat.com/errata/RHSA-2017:2004
- https://insinuator.net/2017/05/git-shell-bypass-by-abusing-less-cve-2017-8386/
- https://kernel.googlesource.com/pub/scm/git/git/+/3ec804490a265f4c418a321428c12f3f18b7eff5
- https://security.gentoo.org/glsa/201706-04
- http://www.debian.org/security/2017/dsa-3848
- http://www.securityfocus.com/bid/98409
- https://access.redhat.com/errata/RHSA-2017:2491
- http://www.ubuntu.com/usn/USN-3287-1
