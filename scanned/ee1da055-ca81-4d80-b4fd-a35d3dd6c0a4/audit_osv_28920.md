# [M] Squid vulnerable to heap corruption in ESI assign

## Summary
Severity: Medium
Advisory: CVE-2024-37894
Aliases: GHSA-wgvf-q977-9xjg
CVSS: 6.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-37894
Type: osv

## Details
Squid is a caching proxy for the Web supporting HTTP, HTTPS, FTP, and more. Due to an Out-of-bounds Write error when assigning ESI variables, Squid is susceptible to a Memory Corruption error. This error can lead to a Denial of Service attack.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00009.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37894.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-wgvf-q977-9xjg
- https://nvd.nist.gov/vuln/detail/CVE-2024-37894
- https://security.netapp.com/advisory/ntap-20240719-0001/
- https://github.com/squid-cache/squid/commit/f411fe7d75197852f0e5ee85027a06d58dd8df4c.patch
