# [M] Missing Authorization in Kibana Leading to Unauthorized Disclosure of Fleet Deployment Metadata

## Summary
Severity: Medium
Advisory: CVE-2026-78603
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-78603
Type: osv

## Details
Missing Authorization (CWE-862) in Kibana can lead to information disclosure via Exploiting Incorrectly Configured Access Control Security Levels (CAPEC-180). An authenticated user holding minimal Elasticsearch privileges could bypass Kibana feature authorization and space access controls, resulting in the unauthorized disclosure of Fleet deployment metadata from the default Kibana space.

## References
- https://discuss.elastic.co/t/kibana-9-4-6-9-5-1-security-update-esa-2026-149/390069
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78603.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78603
