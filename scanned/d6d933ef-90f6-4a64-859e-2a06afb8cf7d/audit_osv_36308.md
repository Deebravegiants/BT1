# [C] CVE-2026-2287

## Summary
Severity: Critical
Advisory: CVE-2026-2287
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-2287
Type: osv

## Details
CrewAI does not properly check that Docker is still running during runtime, and will fall back to a sandbox setting that allows for RCE exploitation.

## References
- https://www.kb.cert.org/vuls/id/221883
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2287.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2287
