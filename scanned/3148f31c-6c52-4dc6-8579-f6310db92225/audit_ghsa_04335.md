# [M] marimo contains a reflected cross-site scripting vulnerability in the notebook page

## Summary
Severity: Medium
Advisory: GHSA-8m59-7xv8-735h
CVE: CVE-2026-54386
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-8m59-7xv8-735h
Type: github-advisory

## Affected
- PyPI: `marimo` — affected >=0 <0.23.9

## Details
marimo before 0.23.9 contains a reflected cross-site scripting vulnerability in the notebook page that allows unauthenticated attackers to inject arbitrary JavaScript by exploiting improper escaping of single quotes in the file query parameter reflected into an inline JavaScript string literal. Attackers can craft a malicious link with a payload beginning with __new__ to bypass the 404 check and inject JavaScript into the page, which executes without Content-Security-Policy restrictions in the origin of a victim's marimo server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-54386
- https://github.com/marimo-team/marimo/pull/9789
- https://github.com/marimo-team/marimo/commit/fdd55c8cf6260ae23bb411dc9d9269def5cf75d6
- https://github.com/marimo-team/marimo
- https://github.com/marimo-team/marimo/releases/tag/0.23.9
- https://www.vulncheck.com/advisories/marimo-xss-via-file-query-parameter-in-assets-py
