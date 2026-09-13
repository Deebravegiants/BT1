# [M] CVE-2021-28662

## Summary
Severity: Medium
Advisory: CVE-2021-28662
Aliases: GHSA-jjq6-mh2h-g39h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-28662
Type: osv

## Details
An issue was discovered in Squid 4.x before 4.15 and 5.x before 5.0.6. If a remote server sends a certain response header over HTTP or HTTPS, there is a denial of service. This header can plausibly occur in benign network traffic.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LSQ3U54ZCNXR44QRPW3AV2VCS6K3TKCF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4EPIWUZDJAXADDHVOPKRBTQHPBR6H66/
- http://seclists.org/fulldisclosure/2023/Oct/14
- http://www.openwall.com/lists/oss-security/2023/10/11/3
- https://www.debian.org/security/2021/dsa-4924
- http://www.squid-cache.org/Versions/v6/changesets/squid-6-051824924c709bd6162a378f746fb859454c674e.patch
- https://github.com/squid-cache/squid/commit/051824924c709bd6162a378f746fb859454c674e
- https://github.com/squid-cache/squid/security/advisories/GHSA-jjq6-mh2h-g39h
