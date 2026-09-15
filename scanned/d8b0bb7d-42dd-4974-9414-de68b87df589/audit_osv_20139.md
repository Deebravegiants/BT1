# [C] CVE-2021-3148

## Summary
Severity: Critical
Advisory: CVE-2021-3148
Aliases: GHSA-ghc2-hx3w-jqmp, PYSEC-2021-55
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-27
Source: https://osv.dev/vulnerability/CVE-2021-3148
Type: osv

## Details
An issue was discovered in SaltStack Salt before 3002.5. Sending crafted web requests to the Salt API can result in salt.utils.thin.gen_thin() command injection because of different handling of single versus double quotes. This is related to salt/utils/thin.py.

## References
- https://github.com/saltstack/salt/releases
- https://lists.debian.org/debian-lts-announce/2021/11/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7GRVZ5WAEI3XFN2BDTL6DDXFS5HYSDVB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FUGLOJ6NXLCIFRD2JTXBYQEMAEF2B6XH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YOGNT2XWPOYV7YT75DN7PS4GIYWFKOK5/
- https://saltproject.io/security_announcements/active-saltstack-cve-release-2021-feb-25/
- https://security.gentoo.org/glsa/202103-01
- https://security.gentoo.org/glsa/202310-22
- https://www.debian.org/security/2021/dsa-5011
