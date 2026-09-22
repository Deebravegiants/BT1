# [H] CVE-2021-28651

## Summary
Severity: High
Advisory: CVE-2021-28651
Aliases: GHSA-ch36-9jhx-phm4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-28651
Type: osv

## Details
An issue was discovered in Squid before 4.15 and 5.x before 5.0.6. Due to a buffer-management bug, it allows a denial of service. When resolving a request with the urn: scheme, the parser leaks a small amount of memory. However, there is an unspecified attack methodology that can easily trigger a large amount of memory consumption.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LSQ3U54ZCNXR44QRPW3AV2VCS6K3TKCF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4EPIWUZDJAXADDHVOPKRBTQHPBR6H66/
- http://seclists.org/fulldisclosure/2023/Oct/14
- http://www.openwall.com/lists/oss-security/2023/10/11/3
- https://lists.debian.org/debian-lts-announce/2021/06/msg00014.html
- https://security.netapp.com/advisory/ntap-20210716-0007/
- https://www.debian.org/security/2021/dsa-4924
- https://bugs.squid-cache.org/show_bug.cgi?id=5104
- https://github.com/squid-cache/squid/security/advisories/GHSA-ch36-9jhx-phm4
