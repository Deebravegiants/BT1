# [H] @electron/packager's build process memory potentially leaked into final executable

## Summary
Severity: High
Advisory: GHSA-34h3-8mw4-qw57
CVE: CVE-2024-29900
CWE: CWE-402
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-34h3-8mw4-qw57
Type: github-advisory

## Affected
- npm: `@electron/packager` — affected >=18.3.0 <18.3.1

## Details
### Impact
A random segment of ~1-10kb of Node.js heap memory allocated either side of a known buffer will be leaked into the final executable. This memory _could_ contain sensitive information such as environment variables, secrets files, etc.

### Patches
This issue is patched in 18.3.1

### Workarounds
No workarounds, please update to a patched version of `@electron/packager` immediately if impacated.

## References
- https://github.com/electron/packager/security/advisories/GHSA-34h3-8mw4-qw57
- https://nvd.nist.gov/vuln/detail/CVE-2024-29900
- https://github.com/electron/packager/commit/d421d4bd3ced889a4143c5c3ab6d95e3be249eee
- https://github.com/electron/packager
