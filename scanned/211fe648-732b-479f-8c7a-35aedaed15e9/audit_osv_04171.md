# [M] BIT-appsmith-2024-55963

## Summary
Severity: Medium
Advisory: BIT-appsmith-2024-55963
Aliases: CVE-2024-55963, GHSA-6mc8-hw5c-7qqr
Ecosystem: Bitnami
Published: 2025-04-02
Source: https://osv.dev/vulnerability/BIT-appsmith-2024-55963
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <1.51.0

## Details
An issue was discovered in Appsmith before 1.51. A user on Appsmith that doesn't have admin permissions can trigger the restart API on Appsmith, causing a server restart. This is still within the Appsmith container, and the impact is limited to Appsmith's own server only, but there is a denial of service because it can be continually restarted. This is due to incorrect access control checks, which should check for super user permissions on the incoming request.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-6mc8-hw5c-7qqr
- https://nvd.nist.gov/vuln/detail/CVE-2024-55963
