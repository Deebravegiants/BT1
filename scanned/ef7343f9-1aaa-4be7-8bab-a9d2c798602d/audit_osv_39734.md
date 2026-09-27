# [M] ClearanceKit's signed policy tables lack monotonic counter, allowing replay of older legitimately-signed snapshots

## Summary
Severity: Medium
Advisory: CVE-2026-47133
Aliases: GHSA-9hx3-5wp9-2qqg
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-47133
Type: osv

## Details
ClearanceKit intercepts file-system access events on macOS and enforces per-process access policies. Prior to version 5.0.10, each table in the on-disk SQLite policy store (`/Library/Application Support/clearancekit/store.db`) is verified using an ECDSA signature stored in the `data_signatures` table. The signed payload contains only the canonical row content, with no version counter or freshness binding. An attacker who can write `store.db` and the matching `data_signatures` row — feasible during the opfilter-update window when the Endpoint Security filter is offline, or via offline-boot / decrypted-backup scenarios — can substitute a previously-captured legitimately-signed snapshot. opfilter accepts the older snapshot as fully valid on next boot because the existing signatures still verify. Version 5.0.10 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47133.json
- https://github.com/craigjbass/clearancekit/security/advisories/GHSA-9hx3-5wp9-2qqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47133
