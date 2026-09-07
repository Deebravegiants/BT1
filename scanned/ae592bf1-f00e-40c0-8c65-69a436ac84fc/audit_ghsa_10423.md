# [M] OpenClaw `node.invoke(browser.proxy)` bypasses `browser.request` persistent profile-mutation guard

## Summary
Severity: Medium
Advisory: GHSA-cmfr-9m2r-xwhq
CVE: CVE-2026-42431
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-cmfr-9m2r-xwhq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

OpenClaw `node.invoke(browser.proxy)` bypasses `browser.request` persistent profile-mutation guard.

node.invoke(browser.proxy) could mutate persistent browser profiles through a path that bypassed the browser.request guard.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= v2026.04.01`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @nicky-cc  of Tencent zhuque Lab ([https://github.com/Tencent/AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard)) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cmfr-9m2r-xwhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42431
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-persistent-profile-mutation-via-node-invoke-browser-proxy-bypass
