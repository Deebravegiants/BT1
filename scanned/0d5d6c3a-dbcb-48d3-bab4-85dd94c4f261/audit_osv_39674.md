# [H] Dash: Users can write to config despire permissions (OIDC tested)

## Summary
Severity: High
Advisory: CVE-2026-46485
Aliases: GHSA-vjj9-fmvr-6h3p
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-46485
Type: osv

## Details
Dashy is a self-hostable personal dashboard. Prior to 4.0.8, Dashy deployments using OIDC can allow unauthenticated users or non-admin authenticated users to write changes to the main config.yaml through the config-saving functionality despite configured permissions, allowing unauthorized modification of dashboard configuration and potential service disruption. This issue is fixed in version 4.0.8.

## References
- https://github.com/lissy93/dashy/releases/tag/4.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46485.json
- https://github.com/lissy93/dashy/security/advisories/GHSA-vjj9-fmvr-6h3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-46485
