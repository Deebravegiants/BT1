# [H] Karakeep has a SSRF Protection Bypass via Redirect Handling

## Summary
Severity: High
Advisory: CVE-2026-45082
Aliases: GHSA-g647-327m-79g9
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-45082
Type: osv

## Details
Karakeep is a elf-hostable bookmark-everything app. A Server-Side Request Forgery (SSRF) protection bypass vulnerability was identified in versions prior to 0.32.0 affecting redirect-following processing components. Although the application implements protections intended to prevent requests toward internal/private network destinations, these protections could be bypassed through crafted HTTP redirect chains. By leveraging attacker-controlled redirects, an authenticated user could cause vulnerable application components to initiate requests toward internally reachable Docker network services accessible from the application environment. The issue affected multiple processing paths, including crawler-related functionality and video download processing flows. Version 0.32.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45082.json
- https://github.com/karakeep-app/karakeep/security/advisories/GHSA-g647-327m-79g9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45082
