# [M] CVE-2021-28116

## Summary
Severity: Medium
Advisory: CVE-2021-28116
Aliases: GHSA-rgf3-9v3p-qp82
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/CVE-2021-28116
Type: osv

## Details
Squid through 4.14 and 5.x through 5.0.5, in some configurations, allows information disclosure because of an out-of-bounds read in WCCP protocol data. This can be leveraged as part of a chain for remote code execution as nobody.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LSQ3U54ZCNXR44QRPW3AV2VCS6K3TKCF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4EPIWUZDJAXADDHVOPKRBTQHPBR6H66/
- http://www.openwall.com/lists/oss-security/2021/10/04/1
- http://www.squid-cache.org/Versions/
- https://github.com/squid-cache/squid/security/advisories/GHSA-rgf3-9v3p-qp82
- https://security.gentoo.org/glsa/202105-14
- https://www.debian.org/security/2022/dsa-5171
- https://www.zerodayinitiative.com/advisories/ZDI-21-157/
