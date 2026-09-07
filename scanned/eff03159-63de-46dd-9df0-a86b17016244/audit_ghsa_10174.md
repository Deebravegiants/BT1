# [M] lodash vulnerable to Prototype Pollution via array path bypass in `_.unset` and `_.omit`

## Summary
Severity: Medium
Advisory: GHSA-f23m-r3pf-42rh
CVE: CVE-2026-2950
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-f23m-r3pf-42rh
Type: github-advisory

## Affected
- npm: `lodash` — affected >=0 <4.18.0
- npm: `lodash-es` — affected >=0 <4.18.0
- npm: `lodash-amd` — affected >=0 <4.18.0
- npm: `lodash.unset` — affected >=4.0.0 <4.18.0

## Details
### Impact

Lodash versions 4.17.23 and earlier are vulnerable to prototype pollution in the `_.unset` and `_.omit` functions. The fix for [CVE-2025-13465](https://github.com/lodash/lodash/security/advisories/GHSA-xxjr-mmjv-4gpg) only guards against string key members, so an attacker can bypass the check by passing array-wrapped path segments. This allows deletion of properties from built-in prototypes such as `Object.prototype`, `Number.prototype`, and `String.prototype`.

The issue permits deletion of prototype properties but does not allow overwriting their original behavior.

### Patches

This issue is patched in 4.18.0.

### Workarounds

None. Upgrade to the patched version.

## References
- https://github.com/lodash/lodash/security/advisories/GHSA-f23m-r3pf-42rh
- https://github.com/lodash/lodash/security/advisories/GHSA-xxjr-mmjv-4gpg
- https://nvd.nist.gov/vuln/detail/CVE-2026-2950
- https://github.com/lodash/lodash
