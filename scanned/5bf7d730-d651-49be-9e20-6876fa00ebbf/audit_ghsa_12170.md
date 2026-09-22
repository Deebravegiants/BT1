# [M] @backstage/plugin-scaffolder-backend: Possible exposure of defaultEnvironment secrets using dry-run endpoint

## Summary
Severity: Medium
Advisory: GHSA-8wq8-6859-qx77
CVE: CVE-2026-32237
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-8wq8-6859-qx77
Type: github-advisory

## Affected
- npm: `@backstage/plugin-scaffolder-backend` — affected >=3.1.0 <3.1.5

## Details
### Impact                                                                                                                                                                         
                                         
  Authenticated users with permission to execute scaffolder dry-runs can gain access to server-configured environment secrets through the dry-run API response. Secrets are properly 
  redacted in log output but not in all parts of the response payload.
                                                                                                                                                                                     
  Deployments that have configured `scaffolder.defaultEnvironment.secrets` are affected.
                          
  ### Patches                            

  This is patched in `@backstage/plugin-scaffolder-backend` version 3.1.5
  ### Workarounds

  Remove or empty the `scaffolder.defaultEnvironment.secrets` configuration from `app-config.yaml`. Alternatively, restrict access to the scaffolder dry-run functionality via the
  permissions framework.

  ### References

  - [Backstage Scaffolder Backend documentation](https://backstage.io/docs/features/software-templates/)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-8wq8-6859-qx77
- https://nvd.nist.gov/vuln/detail/CVE-2026-32237
- https://github.com/backstage/backstage/commit/3b62dd2d6bf7623ebd23e4b5a6dceb209f98dfce
- https://github.com/backstage/backstage
