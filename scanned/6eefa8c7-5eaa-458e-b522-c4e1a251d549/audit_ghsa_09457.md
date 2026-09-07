# [H] Gradio contains a cookie injection vulnerability

## Summary
Severity: High
Advisory: GHSA-7hp7-4p35-3cx2
CVE: CVE-2026-48545
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-7hp7-4p35-3cx2
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <6.15.0

## Details
Gradio before version 6.15.0 contains a cookie injection vulnerability that allows remote attackers to perform cross-Space session fixation by exploiting a shared module-level HTTP client used across all users in the reverse proxy endpoint. Attackers controlling any HF Space can return a parent-domain cookie that the shared client stores and automatically replays into all subsequent proxy requests to other legitimate Spaces, affecting all users of the same Gradio deployment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48545
- https://github.com/gradio-app/gradio/issues/13369
- https://github.com/gradio-app/gradio/pull/13384
- https://github.com/gradio-app/gradio/commit/feb7237d01f359d2ad4ee42d00344e61692b3b39
- https://github.com/gradio-app/gradio
- https://github.com/gradio-app/gradio/releases/tag/gradio@6.15.0
- https://www.vulncheck.com/advisories/gradio-cookie-injection-via-shared-pro
