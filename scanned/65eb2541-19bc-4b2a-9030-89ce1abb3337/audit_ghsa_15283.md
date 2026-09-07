# [M] FastAPI Admin cross-site scripting (XSS) vulnerability in the Create Product function

## Summary
Severity: Medium
Advisory: GHSA-22xm-w7r2-834q
CVE: CVE-2024-42816
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-26
Source: https://github.com/advisories/GHSA-22xm-w7r2-834q
Type: github-advisory

## Affected
- PyPI: `fastapi-admin` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in the Create Product function of fastapi-admin pro v0.1.4 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the Product Name parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42816
- https://github.com/fastapi-admin/fastapi-admin/issues/172
- https://fastapi-admin-pro.long2ice.io/admin/login
- https://github.com/fastapi-admin/fastapi-admin
