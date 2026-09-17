# [M] @digitalocean/do-markdownit has Type Confusion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2h8j-8r9p-849f
CVE: CVE-2025-59717
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-19
Source: https://github.com/advisories/GHSA-2h8j-8r9p-849f
Type: github-advisory

## Affected
- npm: `@digitalocean/do-markdownit` — affected >=0

## Details
### Overview
A type confusion issue exists in the `@digitalocean/do-markdownit` package. In the `callout` and `fence_environment` plugins, the `allowedClasses` and `allowedEnvironments` options are expected to be arrays of strings. If these options are provided as a single string, the code applies `.includes` directly on the string, resulting in substring matching instead of membership checks against an array.

### Affected Versions
All versions up to and including 1.16.1 (npm).

### Impact
Supplying crafted input can bypass intended allow-lists (e.g., class/environment constraints) due to substring checks, which may enable rendering of unintended classes or environments and lead to policy bypass in downstream consumers.

### Mitigation
Until an upstream fix is released, ensure configuration normalization before invoking the plugins:
- Validate that `allowedClasses` and `allowedEnvironments` are arrays (`Array.isArray(...)`), converting single strings into one-element arrays when necessary.
- Consider sanitizing or strictly validating user-controlled values that influence Markdown rendering.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59717
- https://gist.github.com/thesmartshadow/dd19665f1f51a4e3c7a766e70c9eafd0
- https://github.com/digitalocean/do-markdownit
- https://www.npmjs.com/package/@digitalocean/do-markdownit
