# [M] WWBN AVideo affected by CSRF on Site Customization Endpoint Enables Logo Overwrite via Base64 File Write

## Summary
Severity: Medium
Advisory: CVE-2026-35180
Aliases: GHSA-5572-2jgx-fc7c
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35180
Type: osv

## Details
WWBN AVideo is an open source video platform. In versions 26.0 and prior, the site customization endpoint at admin/customize_settings_nativeUpdate.json.php lacks CSRF token validation and writes uploaded logo files to disk before the ORM's domain-based security check executes. Combined with SameSite=None cookie policy, a cross-origin POST can overwrite the platform's logo with attacker-controlled content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35180.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-5572-2jgx-fc7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-35180
