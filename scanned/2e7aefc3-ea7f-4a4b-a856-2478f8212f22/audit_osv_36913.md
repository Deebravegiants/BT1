# [M] Missing Authorization in Kibana Leading to Unauthorized Endpoint Response Action Configuration

## Summary
Severity: Medium
Advisory: CVE-2026-26939
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-26939
Type: osv

## Details
Missing Authorization (CWE-862) in Kibana’s server-side Detection Rule Management can lead to Unauthorized Endpoint Response Action Configuration (host isolation, process termination, and process suspension) via CAPEC-1 (Accessing Functionality Not Properly Constrained by ACLs). This requires an authenticated attacker with rule management privileges.

## References
- https://discuss.elastic.co/t/kibana-8-19-12-9-2-6-9-3-1-security-update-esa-2026-19/385530
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26939.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26939
