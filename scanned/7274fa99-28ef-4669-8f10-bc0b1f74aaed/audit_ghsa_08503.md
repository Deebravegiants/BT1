# [M] Summarize contains a missing authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5624-2pmv-jx46
CVE: CVE-2026-45243
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-5624-2pmv-jx46
Type: github-advisory

## Affected
- npm: `@steipete/summarize` — affected >=0 <0.15.0

## Details
Summarize prior to 0.15.0 contains a missing authorization vulnerability in the content script window.postMessage bridge that allows malicious pages to perform unauthorized operations on automation artifacts. Attackers can simulate runtime messages with spoofed sender identifiers to list, read, create, overwrite, or delete automation artifacts scoped to the affected tab without proper authorization checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45243
- https://github.com/steipete/summarize/pull/222
- https://github.com/steipete/summarize/commit/357544063af535bd574752622f9eb94be33ee5fd
- https://github.com/steipete/summarize
- https://github.com/steipete/summarize/releases/tag/v0.15.1
- https://github.com/steipete/summarize/releases/tag/v0.15.2
- https://www.vulncheck.com/advisories/summarize-browser-extension-missing-authorization-via-content-script
