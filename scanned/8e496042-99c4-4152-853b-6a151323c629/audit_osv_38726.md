# [H] Spring Data REST SpEL Injection via Map Key in JSON Patch

## Summary
Severity: High
Advisory: CVE-2026-41729
Aliases: GHSA-j388-8rm5-p97f
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-41729
Type: osv

## Details
Spring Data REST is vulnerable to SpEL expression injection through map-typed properties when processing JSON Patch (application/json-patch+json) requests. When a persistent entity exposes a Map-typed property, the JSON Pointer path segment used as the map key is embedded directly into a SpEL expression without sanitization or validation.

Affected versions:
Spring Data REST 3.7.0 through 3.7.19; 4.3.0 through 4.3.16; 4.4.0 through 4.4.14; 4.5.0 through 4.5.11; 5.0.0 through 5.0.5.

## References
- https://spring.io/security/cve-2026-41729
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41729.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41729
