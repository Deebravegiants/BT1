# [H] Himmelblau's Kerberos credential cache collection is world readable

## Summary
Severity: High
Advisory: CVE-2025-54882
Aliases: GHSA-phfx-rjfw-wj83
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/CVE-2025-54882
Type: osv

## Details
Himmelblau is an interoperability suite for Microsoft Azure Entra ID and Intune. In versions 0.8.0 through 0.9.21 and 1.0.0-beta through 1.1.0, Himmelblau stores the cloud TGT received during logon in the Kerberos credential cache. The created credential cache collection and received credentials are stored as world readable. This is fixed in versions 0.9.22 and 1.2.0. To work around this issue, remove all read access to Himmelblau caches for all users except for owners.

## References
- https://github.com/himmelblau-idm/himmelblau/releases/tag/0.9.22
- https://github.com/himmelblau-idm/himmelblau/releases/tag/1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54882.json
- https://github.com/himmelblau-idm/himmelblau/security/advisories/GHSA-phfx-rjfw-wj83
- https://nvd.nist.gov/vuln/detail/CVE-2025-54882
- https://github.com/himmelblau-idm/himmelblau/commit/b562053df3dffb1dd9ab3d09af986886773be2ad
- https://github.com/himmelblau-idm/himmelblau/commit/faae58b0384aca8b21b4be5f1c507412eec3778a
