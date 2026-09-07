# [H] React Router: RSC Mode CSRF Bypass Allows Action Execution Before 400 Response

## Summary
Severity: High
Advisory: GHSA-qwww-vcr4-c8h2
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-qwww-vcr4-c8h2
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.12.0 <7.18.2
- npm: `react-router` — affected >=8.0.0 <8.3.0

## Details
This is a follow up to CVE-2026-22030 to address related CSRF flows in unstable RSC code paths.

> [!NOTE]
> This only affects your application if you are using the unstable RSC APIs

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-qwww-vcr4-c8h2
- https://github.com/remix-run/react-router/pull/15353
- https://github.com/remix-run/react-router/commit/7a71c728ad116bd78699a258b2014ce9585729f5
- https://github.com/remix-run/react-router/commit/8ebd5df9932854547963e3255c8454e62430e05d
- https://github.com/remix-run/react-router
- https://github.com/remix-run/react-router/blob/main/CHANGELOG.md#v830
- https://github.com/remix-run/react-router/blob/v7/CHANGELOG.md#v7182
- https://github.com/remix-run/react-router/releases/tag/react-router%407.18.2
- https://github.com/remix-run/react-router/releases/tag/react-router@8.3.0
- http://github.com/remix-run/react-router/pull/15311
