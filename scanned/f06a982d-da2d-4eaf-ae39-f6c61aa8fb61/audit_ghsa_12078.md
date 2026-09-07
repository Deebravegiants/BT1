# [M] Gradio has an Open Redirect in its OAuth Flow

## Summary
Severity: Medium
Advisory: GHSA-pfjf-5gxr-995x
CVE: CVE-2026-28415
CWE: CWE-200, CWE-284, CWE-330, CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-pfjf-5gxr-995x
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <6.6.0

## Details
# Summary

The _redirect_to_target() function in Gradio's OAuth flow accepts an unvalidated _target_url query parameter, allowing redirection to arbitrary external URLs. This affects the /logout and /login/callback endpoints on Gradio apps with OAuth enabled (i.e. apps running on Hugging Face Spaces with gr.LoginButton).

## Details

```python

  def _redirect_to_target(request, default_target="/"):
      target = request.query_params.get("_target_url", default_target)
      return RedirectResponse(target)  # No validation
```
  An attacker can craft a URL like https://my-space.hf.space/logout?_target_url=https://evil.com/phishing that redirects the user to an external site after logout. Because the URL originates from a trusted hf.space domain, users are more likely to trust the link.

## Impact

Phishing — an attacker can use the trusted domain to redirect users to a malicious site. No direct data exposure or server-side impact.

 ## Fix
The _target_url parameter is now sanitized to only use the path, query, and fragment, stripping any scheme or host.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-pfjf-5gxr-995x
- https://nvd.nist.gov/vuln/detail/CVE-2026-28415
- https://github.com/gradio-app/gradio/commit/dfee0da06d0aa94b3c2684131e7898d5d5c1911e
- https://github.com/gradio-app/gradio
- https://github.com/gradio-app/gradio/releases/tag/gradio%406.6.0
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2026-65.yaml
