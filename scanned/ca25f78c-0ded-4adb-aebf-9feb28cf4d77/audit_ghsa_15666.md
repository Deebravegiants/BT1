# [M] Khoj Open Redirect Vulnerability in Login Page

## Summary
Severity: Medium
Advisory: GHSA-564j-v29w-rqr6
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-564j-v29w-rqr6
Type: github-advisory

## Affected
- PyPI: `khoj-assistant` — affected >=0 <1.14.0

## Details
### Summary
An attacker can use the `next` parameter on the login page to redirect a victim to a malicious page, while masking this using a legit-looking `app.khoj.dev` url.
For example, `https://app.khoj.dev/login?next=//example.com` will redirect to the https://example.com page.

### Details
The problem seems to be in this method: https://github.com/khoj-ai/khoj/blob/2667ef45449eb408ce1d7c393be04845be31e15f/src/khoj/routers/auth.py#L95

### PoC
Open the `https://app.khoj.dev/login?next=//example.com` url in a Gecko-based browser (Firefox).

### Impact
The impact is low, and this could only be used in phishing attempts, but it's still a problem nonetheless.

## References
- https://github.com/khoj-ai/khoj/security/advisories/GHSA-564j-v29w-rqr6
- https://github.com/khoj-ai/khoj/commit/4daf16e5f916641304e11d56a6071ad365c21a18
- https://github.com/khoj-ai/khoj
- https://github.com/khoj-ai/khoj/blob/2667ef45449eb408ce1d7c393be04845be31e15f/src/khoj/routers/auth.py#L95
