# [H] Open WebUI lacks authentication for the `api/v1/utils/pdf` endpoint

## Summary
Severity: High
Advisory: GHSA-9vf8-xgwm-97r8
CVE: CVE-2024-8053
CWE: CWE-287, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-9vf8-xgwm-97r8
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
In version v0.3.10 of open-webui/open-webui, the `api/v1/utils/pdf` endpoint lacks authentication mechanisms, allowing unauthenticated attackers to access the PDF generation service. This vulnerability can be exploited by sending a POST request with an excessively large payload, potentially leading to server resource exhaustion and denial of service (DoS). Additionally, unauthorized users can misuse the endpoint to generate PDFs without verification, resulting in service misuse and potential operational and financial impacts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8053
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/ebe8c1fa-113b-4df9-be03-a406b9adb9f4
