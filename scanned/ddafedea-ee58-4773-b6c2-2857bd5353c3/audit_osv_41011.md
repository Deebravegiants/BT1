# [M] Grav Flex Objects 1.4.0 through 1.4.7 Authorization Bypass via Shortcode

## Summary
Severity: Medium
Advisory: CVE-2026-56707
Aliases: GHSA-x929-528m-vx2m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-56707
Type: osv

## Details
Grav Flex Objects plugin versions 1.4.0 through 1.4.7 contain an authorization bypass vulnerability in the flex-objects shortcode that allows users with page-edit access to render any registered Flex collection without permission checks. Attackers can place the shortcode in published pages to expose sensitive directory contents including user account information, bypassing the authorize ACL enforced in the admin panel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56707.json
- https://github.com/getgrav/grav/security/advisories/GHSA-x929-528m-vx2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-56707
- https://www.vulncheck.com/advisories/grav-flex-objects-through-authorization-bypass-via-shortcode
