# [M] Loki Path Traversal - CVE-2021-36156 Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-21726
Aliases: GHSA-497x-rrr9-68jp, GO-2026-5115
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/CVE-2026-21726
Type: osv

## Details
The CVE-2021-36156 fix validates the namespace parameter for path traversal sequences after a single URL decode, by double encoding, an attacker can read files at the Ruler API endpoint /loki/api/v1/rules/{namespace}

Thanks to Prasanth Sundararajan for reporting this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21726.json
- https://grafana.com/security/security-advisories/cve-2026-21726
- https://nvd.nist.gov/vuln/detail/CVE-2026-21726
