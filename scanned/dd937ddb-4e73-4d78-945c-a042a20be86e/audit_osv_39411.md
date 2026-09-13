# [H] Roxy-WI: Authentication bypass via 'api' substring in URL + unauthenticated /api/gpt

## Summary
Severity: High
Advisory: CVE-2026-45567
Aliases: GHSA-4fcm-qgg8-w2vf
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45567
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, there is an authentication bypass vulnerability via 'api' substring in URL + unauthenticated /api/gpt. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45567.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-4fcm-qgg8-w2vf
- https://nvd.nist.gov/vuln/detail/CVE-2026-45567
