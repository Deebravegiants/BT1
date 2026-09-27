# [M] CVE-2021-31806

## Summary
Severity: Medium
Advisory: CVE-2021-31806
Aliases: CVE-2021-31807, CVE-2021-31808, GHSA-pxwq-f3qr-w2xf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-31806
Type: osv

## Details
An issue was discovered in Squid before 4.15 and 5.x before 5.0.6. Due to a memory-management bug, it is vulnerable to a Denial of Service attack (against all clients using the proxy) via HTTP Range request processing.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LSQ3U54ZCNXR44QRPW3AV2VCS6K3TKCF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4EPIWUZDJAXADDHVOPKRBTQHPBR6H66/
- http://seclists.org/fulldisclosure/2023/Oct/14
- http://www.openwall.com/lists/oss-security/2023/10/11/3
- https://lists.debian.org/debian-lts-announce/2021/06/msg00014.html
- https://security.netapp.com/advisory/ntap-20210716-0007/
- https://www.debian.org/security/2021/dsa-4924
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-e7cf864f938f24eea8af0692c04d16790983c823.patch
- https://github.com/squid-cache/squid/security/advisories/GHSA-pxwq-f3qr-w2xf
