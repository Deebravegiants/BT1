# [M] RomM vulnerable to Authenticated Path Traversal

## Summary
Severity: Medium
Advisory: CVE-2025-53908
Aliases: GHSA-fx9g-xw4j-jwc3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/CVE-2025-53908
Type: osv

## Details
RomM is a self-hosted rom manager and player. Versions prior to 3.10.3 and 4.0.0-beta.3 have an authenticated path traversal vulnerability in the `/api/raw` endpoint. Anyone running the latest version of RomM and has multiple users, even unprivileged users, such as the kiosk user in the official implementation, may be affected. This allows the leakage of passwords and users that may be stored on the system. Versions 3.10.3 and 4.0.0-beta.3 contain a patch.

## References
- https://github.com/rommapp/romm/blob/4.0.0-beta.2/backend/endpoints/raw.py#L31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53908.json
- https://github.com/rommapp/romm/security/advisories/GHSA-fx9g-xw4j-jwc3
- https://nvd.nist.gov/vuln/detail/CVE-2025-53908
- https://github.com/rommapp/romm/commit/7c94cb05e74ddb6a6af7b82320686c01754e9966
- https://github.com/rommapp/romm/commit/baa1a9759079c36e36a9f10c920c46b57d0b6151
