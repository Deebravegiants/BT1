# [C] Squid's URN Handling can lead to Buffer Overflow

## Summary
Severity: Critical
Advisory: CVE-2025-54574
Aliases: GHSA-w4gv-vw3f-29g3
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:H)
Published: 2025-08-01
Source: https://osv.dev/vulnerability/CVE-2025-54574
Type: osv

## Details
Squid is a caching proxy for the Web. In versions 6.3 and below, Squid is vulnerable to a heap buffer overflow and possible remote code execution attack when processing URN due to incorrect buffer management. This has been fixed in version 6.4. To work around this issue, disable URN access permissions.

## References
- http://www.openwall.com/lists/oss-security/2025/11/05/5
- https://github.com/squid-cache/squid/releases/tag/SQUID_6_4
- https://lists.debian.org/debian-lts-announce/2025/09/msg00027.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54574.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-w4gv-vw3f-29g3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54574
- https://github.com/squid-cache/squid/commit/a27bf4b84da23594150c7a86a23435df0b35b988
