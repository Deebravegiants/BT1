# [M] CycloneDX cdxgen may execute code contained within build-related files

## Summary
Severity: Medium
Advisory: GHSA-hxf3-vgpm-fv9p
CVE: CVE-2024-50611
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-28
Source: https://github.com/advisories/GHSA-hxf3-vgpm-fv9p
Type: github-advisory

## Affected
- npm: `@cyclonedx/cdxgen` — affected >=0 <11.1.7

## Details
CycloneDX cdxgen prior to 11.1.7, when run against an untrusted codebase, may execute code contained within build-related files such as build.gradle.kts, a similar issue to CVE-2022-24441. cdxgen is used by, for example, OWASP dep-scan. NOTE: this has been characterized as a design limitation, rather than an implementation mistake.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-50611
- https://github.com/CycloneDX/cdxgen/issues/1328
- https://github.com/CycloneDX/cdxgen/pull/1614
- https://github.com/CycloneDX/cdxgen
- https://github.com/CycloneDX/cdxgen/releases
- https://github.com/CycloneDX/cdxgen/releases/tag/v11.1.7
- https://owasp.org/www-project-dep-scan
