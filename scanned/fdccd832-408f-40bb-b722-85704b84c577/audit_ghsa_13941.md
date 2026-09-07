# [M] Mayan EDMS DMS XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5m6v-2xgf-qhrw
CVE: CVE-2022-47419
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-5m6v-2xgf-qhrw
Type: github-advisory

## Affected
- PyPI: `mayan-edms` — affected >=0 <4.3.6

## Details
An XSS vulnerability was discovered in the Mayan EDMS DMS. Successful XSS exploitation was observed in the in-product tagging system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47419
- https://github.com/mayan-edms/Mayan-EDMS
- https://github.com/pypa/advisory-database/tree/main/vulns/mayan-edms/PYSEC-2023-276.yaml
- https://www.mayan-edms.com/news/2023/02/version-4.3.6
- https://www.rapid7.com/blog/post/2023/02/07/multiple-dms-xss-cve-2022-47412-through-cve-20222-47419
