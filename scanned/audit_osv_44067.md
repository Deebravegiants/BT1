# [M] Incorrect Authorization in Kibana Leading to Unauthorized Cross-Space Exposure of Machine Learning Job Data

## Summary
Severity: Medium
Advisory: CVE-2026-78598
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-78598
Type: osv

## Details
Incorrect Authorization (CWE-863) in the Kibana machine learning feature can lead to information disclosure via Exploiting Incorrectly Configured Access Control Security Levels (CAPEC-180). An authenticated user holding machine learning job management privileges within a single Kibana space could cause a job's saved object to become accessible across all spaces in the Kibana instance, without holding access rights to those additional spaces.

## References
- https://discuss.elastic.co/t/kibana-8-19-19-9-3-8-9-4-4-security-update-esa-2026-156/390111
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78598.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78598
