# [C] builderio/qwik is vulnerable to code injection

## Summary
Severity: Critical
Advisory: GHSA-9wf9-qvvp-2929
CVE: CVE-2023-1283
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-09
Source: https://github.com/advisories/GHSA-9wf9-qvvp-2929
Type: github-advisory

## Affected
- npm: `@builder.io/qwik` — affected >=0 <0.21.0

## Details
Code Injection in GitHub repository builderio/qwik prior to 0.21.0. The Function deserializer can be accessed using the pureServerFunction feature. This allows any Javascript code to be run by node.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1283
- https://github.com/BuilderIO/qwik/pull/3249/commits/4d9ba6e098ae6e537aa55abb6b8369bb670ffe66
- https://github.com/builderio/qwik/commit/4d9ba6e098ae6e537aa55abb6b8369bb670ffe66
- https://github.com/BuilderIO/qwik
- https://huntr.dev/bounties/63f1ff91-48f3-4886-a179-103f1ddd8ff8
