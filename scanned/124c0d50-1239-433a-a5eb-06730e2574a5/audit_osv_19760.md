# [C] CVE-2021-25281

## Summary
Severity: Critical
Advisory: CVE-2021-25281
Aliases: GHSA-xxw3-765m-f37p, PYSEC-2021-50
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-27
Source: https://osv.dev/vulnerability/CVE-2021-25281
Type: osv

## Details
An issue was discovered in through SaltStack Salt before 3002.5. salt-api does not honor eauth credentials for the wheel_async client. Thus, an attacker can remotely run any wheel modules on the master.

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
- https://www.saltstack.com/blog/active-saltstack-cve-announced-2021-jan-21/
- http://packetstormsecurity.com/files/162058/SaltStack-Salt-API-Unauthenticated-Remote-Command-Execution.html
