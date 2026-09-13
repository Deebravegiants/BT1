# [H] Gradios's CORS origin validation is not performed when the request has a cookie

## Summary
Severity: High
Advisory: GHSA-3c67-5hwx-f6wx
CVE: CVE-2024-47084
CWE: CWE-285, CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-3c67-5hwx-f6wx
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.44.0

## Details
### Impact
**What kind of vulnerability is it? Who is impacted?**

This vulnerability is related to **CORS origin validation**, where the Gradio server fails to validate the request origin when a cookie is present. This allows an attacker’s website to make unauthorized requests to a local Gradio server. Potentially, attackers can upload files, steal authentication tokens, and access user data if the victim visits a malicious website while logged into Gradio. This impacts users who have deployed Gradio locally and use basic authentication.

### Patches
Yes, please upgrade to `gradio>=4.44` to address this issue.

### Workarounds
**Is there a way for users to fix or remediate the vulnerability without upgrading?**

As a workaround, users can manually enforce stricter CORS origin validation by modifying the `CustomCORSMiddleware` class in their local Gradio server code. Specifically, they can bypass the condition that skips CORS validation for requests containing cookies to prevent potential exploitation.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-3c67-5hwx-f6wx
- https://nvd.nist.gov/vuln/detail/CVE-2024-47084
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-196.yaml
