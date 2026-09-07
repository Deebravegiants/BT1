# [M] Scrypted Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xmhh-xrcc-mx36
CVE: CVE-2023-47620
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-xmhh-xrcc-mx36
Type: github-advisory

## Affected
- npm: `@scrypted/server` — affected >=0

## Details
Scrypted is a home video integration and automation platform. In versions 0.55.0 and prior, a reflected cross-site scripting vulnerability exists in the plugin-http.ts file via the `owner' and 'pkg` parameters. An attacker can run arbitrary JavaScript code. As of time of publication, no known patches are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47620
- https://github.com/koush/scrypted
- https://github.com/koush/scrypted/blob/71cbe83a2a20f743342df695ca7b98482b73e60f/server/src/plugin/plugin-http.ts#L45
- https://securitylab.github.com/advisories/GHSL-2023-218_GHSL-2023-219_scrypted
