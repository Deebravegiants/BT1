# [M] Open WebUI Vulnerable to Cross-Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-p5vx-9hj8-cf4h
CVE: CVE-2024-7035
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-p5vx-9hj8-cf4h
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
In version v0.3.8 of open-webui/open-webui, sensitive actions such as deleting and resetting are performed using the GET method. This vulnerability allows an attacker to perform Cross-Site Request Forgery (CSRF) attacks, where an unaware user can unintentionally perform sensitive actions by simply visiting a malicious site or through top-level navigation. The affected endpoints include /rag/api/v1/reset, /rag/api/v1/reset/db, /api/v1/memories/reset, and /rag/api/v1/reset/uploads. This impacts both the availability and integrity of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7035
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/2ac81740-410b-467a-9244-75d82a6f9e11
