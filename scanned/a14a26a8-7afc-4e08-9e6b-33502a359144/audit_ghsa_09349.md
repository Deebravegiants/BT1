# [M] Backstage: Catalog unprocessed read endpoints allow authenticated cross-owner data access without permission checks

## Summary
Severity: Medium
Advisory: GHSA-p7g9-rp3g-mgfg
CVE: CVE-2026-44374
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-p7g9-rp3g-mgfg
Type: github-advisory

## Affected
- npm: `@backstage/plugin-catalog-unprocessed-entities-common` — affected >=0 <0.0.15
- npm: `@backstage/plugin-catalog-unprocessed-entities` — affected >=0 <0.2.30
- npm: `@backstage/plugin-catalog-backend-module-unprocessed` — affected >=0 <0.6.11

## Details
### Impact   

  The unprocessed entities read endpoints in `@backstage/plugin-catalog-backend-module-unprocessed` do not enforce permission authorization checks. Any authenticated user can access unprocessed entity records regardless of ownership. This is 
  an information disclosure vulnerability affecting Backstage installations using this module.                                                                     
                                                                        
  ### Patches             
                                         
  This is patched in `@backstage/plugin-catalog-backend-module-unprocessed` version 0.6.11, `@backstage/plugin-catalog-unprocessed-entities-common` version 0.0.15 and `@backstage/plugin-catalog-unprocessed-entities` version 0.2.30. Users should upgrade all packages.                                    
   
  ### Workarounds                                                                                                                                                                                                                                  
                                                                        
  If users cannot upgrade, they can remove the `@backstage/plugin-catalog-backend-module-unprocessed` module from their backend until the patch is applied. There is no configuration-based workaround to add permission checks to these endpoints    
  without upgrading.

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-p7g9-rp3g-mgfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44374
- https://github.com/backstage/backstage
