# [H] React Router vulnerable to XSS in unstable RSC redirect handling via javascript: redirect targets

## Summary
Severity: High
Advisory: GHSA-8646-j5j9-6r62
CVE: CVE-2026-33245
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-8646-j5j9-6r62
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.7.0 <7.13.2

## Details
When using React Router v7's unstable RSC APIs, there exists a potential client-side XSS issue in the RSC redirect handling if redirects are coming from untrusted sources

> [!NOTE]
> This only impacts your application if you are using the unstable RSC APIs in React Router.

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-8646-j5j9-6r62
- https://nvd.nist.gov/vuln/detail/CVE-2026-33245
- https://github.com/remix-run/react-router
