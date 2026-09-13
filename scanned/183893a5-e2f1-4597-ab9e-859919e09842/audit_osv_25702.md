# [C] CVE-2023-42282

## Summary
Severity: Critical
Advisory: CVE-2023-42282
Aliases: GHSA-78xj-cgh5-2h22
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-08
Source: https://osv.dev/vulnerability/CVE-2023-42282
Type: osv

## Details
The ip package before 1.1.9 for Node.js might allow SSRF because some IP addresses (such as 0x7f.1) are improperly categorized as globally routable via isPublic.

## References
- https://cosmosofcyberspace.github.io/npm_ip_cve/npm_ip_cve.html
- https://huntr.com/bounties/bfc3b23f-ddc0-4ee7-afab-223b07115ed3/
- https://www.bleepingcomputer.com/news/security/dev-rejects-cve-severity-makes-his-github-repo-read-only/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42282.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-42282
- https://security.netapp.com/advisory/ntap-20240315-0008/
- https://github.com/indutny/node-ip/commit/6a3ada9b471b09d5f0f5be264911ab564bf67894
