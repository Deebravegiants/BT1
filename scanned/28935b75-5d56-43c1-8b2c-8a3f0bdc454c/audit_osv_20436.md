# [M] CVE-2021-33620

## Summary
Severity: Medium
Advisory: CVE-2021-33620
Aliases: GHSA-572g-rvwr-6c7f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2021-33620
Type: osv

## Details
Squid before 4.15 and 5.x before 5.0.6 allows remote servers to cause a denial of service (affecting availability to all clients) via an HTTP response. The issue trigger is a header that can be expected to exist in HTTP traffic without any malicious intent by the server.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LSQ3U54ZCNXR44QRPW3AV2VCS6K3TKCF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4EPIWUZDJAXADDHVOPKRBTQHPBR6H66/
- http://seclists.org/fulldisclosure/2023/Oct/14
- http://www.openwall.com/lists/oss-security/2023/10/11/3
- https://lists.debian.org/debian-lts-announce/2021/06/msg00014.html
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-1e05a85bd28c22c9ca5d3ac9f5e86d6269ec0a8c.patch
- http://www.squid-cache.org/Versions/v5/changesets/squid-5-8af775ed98bfd610f9ce762fe177e01b2675588c.patch
- https://github.com/squid-cache/squid/security/advisories/GHSA-572g-rvwr-6c7f
