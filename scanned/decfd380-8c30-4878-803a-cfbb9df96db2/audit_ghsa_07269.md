# [M] React Router: Arbitrary Constructor Injection via deserializeErrors() in React Router SSR Hydration

## Summary
Severity: Medium
Advisory: GHSA-337j-9hxr-rhxg
CVE: CVE-2026-53666
CWE: CWE-470
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-337j-9hxr-rhxg
Type: github-advisory

## Affected
- npm: `react-router` — affected >=6.4.0 <7.18.0

## Details
If application code allows attacker supplied input to overwrite certain aspects of errors caught by the SSR process, then it was possible for attacker to trigger unexpected constructor execution on the client which would trigger outbound network traffic.  This is only possible with very specific (and unlikely) application layer code.

> [!NOTE]
> This does not impact your application if you are using Declarative Mode.  This only impacts Framework Mode and Data Mode applications doing manual SSR/hydration

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-337j-9hxr-rhxg
- https://github.com/remix-run/react-router/pull/15175
- https://github.com/remix-run/react-router/commit/9d22943fd46c8ae4b08236425fa3549e10e9ad1a
- https://github.com/remix-run/react-router
- https://github.com/remix-run/react-router/blob/main/CHANGELOG.md#v7180
- https://github.com/remix-run/react-router/releases/tag/react-router@7.18.0
