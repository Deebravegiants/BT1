# [M] BigSweetPotatoStudio HyperChat has a Server-Side Request Forgery issue

## Summary
Severity: Medium
Advisory: GHSA-r2jq-4h3x-rfj6
CVE: CVE-2026-7223
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-r2jq-4h3x-rfj6
Type: github-advisory

## Affected
- npm: `@dadigua/hyperchat` — affected >=0

## Details
A vulnerability was identified in BigSweetPotatoStudio HyperChat up to 2.0.0-alpha.63. Affected by this issue is the function fetch of the file packages/core/src/http/aiProxyMiddleware.mts of the component AI Proxy Middleware. Such manipulation of the argument baseurl leads to server-side request forgery. The attack can be launched remotely. The exploit is publicly available and might be used. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7223
- https://github.com/BigSweetPotatoStudio/HyperChat/issues/142
- https://github.com/BigSweetPotatoStudio/HyperChat
- https://vuldb.com/submit/802265
- https://vuldb.com/vuln/359823
- https://vuldb.com/vuln/359823/cti
