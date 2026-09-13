# [M] Appsmith's Broken Access Control Allows Viewer Role User to Query Datasources

## Summary
Severity: Medium
Advisory: BIT-appsmith-2024-55604
Aliases: BIT-appsmith-2024-55965, CVE-2024-55604, CVE-2024-55965, GHSA-794x-gm8v-2wj6
Ecosystem: Bitnami
Published: 2025-04-14
Source: https://osv.dev/vulnerability/BIT-appsmith-2024-55604
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <1.51.0

## Details
Appsmith is a platform to build admin panels, internal tools, and dashboards. Users invited as "App Viewer" should not have access to development information of a workspace. Datasources are such a component in a workspace. Yet, in versions of Appsmith prior to 1.51, app viewers are able to get a list of datasources in a workspace they're a member of. This information disclosure does NOT expose sensitive data in the datasources, such as database passwords and API Keys. The attacker needs to have been invited to a workspace as a "viewer", by someone in that workspace with access to invite. The attacker then needs to be able to signup/login to that Appsmith instance. The issue is patched in version 1.51. No known workarounds are available.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-794x-gm8v-2wj6
- https://nvd.nist.gov/vuln/detail/CVE-2024-55604
