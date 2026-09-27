# [C] thlorenz browserify-shim vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-866w-wm4h-95c6
CVE: CVE-2022-37617
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-866w-wm4h-95c6
Type: github-advisory

## Affected
- npm: `browserify-shim` — affected >=0 <3.8.16

## Details
Prototype pollution vulnerability in function `resolveShims` in resolve-shims.js in thlorenz browserify-shim 3.8.15 via the `k` variable in resolve-shims.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37617
- https://github.com/thlorenz/browserify-shim/issues/245
- https://github.com/thlorenz/browserify-shim/pull/246
- https://github.com/thlorenz/browserify-shim/commit/97855e622b6dcd117c77e6583701962ff45e7338
- https://github.com/thlorenz/browserify-shim
- https://github.com/thlorenz/browserify-shim/blob/464b32bbe142664cd9796059798f6c738ea3de8f/lib/resolve-shims.js#L130
- https://github.com/thlorenz/browserify-shim/blob/464b32bbe142664cd9796059798f6c738ea3de8f/lib/resolve-shims.js#L158
