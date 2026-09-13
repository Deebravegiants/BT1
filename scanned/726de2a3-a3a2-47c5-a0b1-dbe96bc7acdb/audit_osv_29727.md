# [H] Squid Denial of Service

## Summary
Severity: High
Advisory: CVE-2024-45802
Aliases: GHSA-f975-v7qw-q7hj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-28
Source: https://osv.dev/vulnerability/CVE-2024-45802
Type: osv

## Details
Squid is an open source caching proxy for the Web supporting HTTP, HTTPS, FTP, and more. Due to Input Validation, Premature Release of Resource During Expected Lifetime, and Missing Release of Resource after Effective Lifetime bugs, Squid is vulnerable to Denial of Service attacks by a trusted server against all clients using the proxy. This bug is fixed in the default build configuration of Squid version 6.10.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00009.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45802.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-f975-v7qw-q7hj
- https://nvd.nist.gov/vuln/detail/CVE-2024-45802
- https://security.netapp.com/advisory/ntap-20250103-0004/
