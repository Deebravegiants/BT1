# [M] Immich Locked Assets Remain Readable Through Albums and Shared Links

## Summary
Severity: Medium
Advisory: CVE-2026-82272
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82272
Type: osv

## Details
Immich through 3.1.0 fails to properly enforce locked asset visibility when assets are locked through the single-asset endpoint, allowing them to remain accessible through shared albums and links. Attackers can read locked assets and their metadata by accessing existing shared albums or links, bypassing the locked visibility protection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82272.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82272
- https://www.vulncheck.com/advisories/immich-locked-assets-remain-readable-through-albums-and-shared-links
- https://github.com/immich-app/immich/issues/29526
- https://github.com/immich-app/immich
- https://github.com/immich-app/immich/blob/6b478924b25768dfea304ec3b8273b8316903304/server/src/repositories/access.repository.ts
- https://github.com/immich-app/immich/blob/6b478924b25768dfea304ec3b8273b8316903304/server/src/services/asset.service.ts
