# [M] Hono vulnerable to XSS through ErrorBoundary component 

## Summary
Severity: Medium
Advisory: GHSA-9r54-q6cx-xmh5
CVE: CVE-2026-24771
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-9r54-q6cx-xmh5
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.11.7

## Details
## Summary

A Cross-Site Scripting (XSS) vulnerability exists in the `ErrorBoundary` component of the hono/jsx library. Under certain usage patterns, untrusted user-controlled strings may be rendered as raw HTML, allowing arbitrary script execution in the victim's browser.

## Details

The issue is in the `ErrorBoundary` component (`src/jsx/components.ts`). `ErrorBoundary` previously forced certain rendered output paths to be treated as raw HTML, bypassing the library's default escaping behavior. This could result in unescaped rendering when developers pass user-controlled strings directly as children, or when fallbackRender returns user-controlled strings (for example, reflecting error messages that contain attacker input).

This vulnerability is only exploitable when an application renders untrusted user input within `ErrorBoundary` without appropriate escaping or sanitization.

## Impact

Successful exploitation may allow attackers to execute arbitrary JavaScript in the victim’s browser (reflected XSS). Depending on the application context, this can lead to actions such as session compromise, data exfiltration, or performing unauthorized actions as the victim.

## Affected Components

* hono/jsx: `ErrorBoundary` component

## References
- https://github.com/honojs/hono/security/advisories/GHSA-9r54-q6cx-xmh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-24771
- https://github.com/honojs/hono/commit/2cf60046d730df9fd0aba85178f3ecfe8212d990
- https://github.com/honojs/hono
