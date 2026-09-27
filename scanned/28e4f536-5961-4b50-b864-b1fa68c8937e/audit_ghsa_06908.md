# [M] SvelteKit: Prototype pollution in file input deletion path in remote-function forms

## Summary
Severity: Medium
Advisory: GHSA-866w-xmhq-wj7x
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-866w-xmhq-wj7x
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=0 <2.69.1

## Details
If you use remote form functions, have an input field of type `file`, and accept arbitrary user-controlled path names for the field, then you are vulnerable to a prototype pollution attack where the attacker can remove e.g. methods on the prototype.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-866w-xmhq-wj7x
- https://github.com/sveltejs/kit/pull/16218
- https://github.com/sveltejs/kit/commit/df32f6fe86cdd0b68b650e3e4631e5896453dcd3
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/@sveltejs/kit@2.69.1
- https://github.com/sveltejs/kit/releases/tag/@sveltejs/kit@3.0.0-next.7
