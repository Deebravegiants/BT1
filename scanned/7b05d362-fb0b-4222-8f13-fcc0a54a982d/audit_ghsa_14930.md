# [M] Open redirect in gradio

## Summary
Severity: Medium
Advisory: GHSA-g6c9-f4xm-9j4x
CVE: CVE-2024-4940
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-22
Source: https://github.com/advisories/GHSA-g6c9-f4xm-9j4x
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0

## Details
An open redirect vulnerability exists in the gradio-app/gradio, affecting the latest version. The vulnerability allows an attacker to redirect users to arbitrary websites, which can be exploited for phishing attacks, Cross-site Scripting (XSS), Server-Side Request Forgery (SSRF), amongst others. This issue is due to improper validation of user-supplied input in the handling of URLs. Attackers can exploit this vulnerability by crafting a malicious URL that, when processed by the application, redirects the user to an attacker-controlled web page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4940
- https://github.com/gradio-app/gradio
- https://huntr.com/bounties/35aaea93-6895-4f03-9c1b-cd992665aa60
