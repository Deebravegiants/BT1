# [M] Gradio Vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-7v2w-h4gh-w5cv
CVE: CVE-2024-8021
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-7v2w-h4gh-w5cv
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0

## Details
An open redirect vulnerability exists in the latest version of gradio-app/gradio. The vulnerability allows an attacker to redirect users to a malicious website by URL encoding. This can be exploited by sending a crafted request to the application, which results in a 302 redirect to an attacker-controlled site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8021
- https://github.com/gradio-app/gradio
- https://huntr.com/bounties/adc23067-ec04-47ef-9265-afd452071888
