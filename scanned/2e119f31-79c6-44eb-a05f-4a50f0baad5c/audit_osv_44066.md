# [M] Missing Authorization in Kibana Entity Store Leading to Unauthorized API Key Creation

## Summary
Severity: Medium
Advisory: CVE-2026-78597
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-78597
Type: osv

## Details
Missing Authorization (CWE-862) in the Kibana Entity Store feature can lead to unauthorized credential creation via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). An authenticated user holding only low-privilege Security feature access could invoke an administrative operation that creates and persists Elasticsearch API keys under the caller's identity, bypassing the elevated cluster and Kibana privileges that the documented Entity Store setup flow requires.

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-security-update-esa-2026-155/390072
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78597.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78597
