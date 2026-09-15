# [M] Runtipi: Authenticated arbitrary file write via backup restore symlink planting

## Summary
Severity: Medium
Advisory: CVE-2026-55168
Aliases: GHSA-wcrf-g9p9-2wg7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-55168
Type: osv

## Details
Runtipi is a personal homeserver orchestrator. In 4.10.0 and earlier, Runtipi accepts symbolic links from an attacker-controlled backup archive and copies them into live application paths during the backup restore flow. An authenticated attacker can plant user-config/app.env as a symlink to an arbitrary reachable path and then send PUT /api/user-config/demoapp3:_user with attacker-controlled appEnv content. FilesystemService.writeTextFile() follows the planted link, allowing content to be written outside the intended restore and user-config directory boundary with Runtipi process permissions. This issue is fixed in version 4.10.1.

## References
- https://github.com/runtipi/runtipi/releases/tag/v4.10.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55168.json
- https://github.com/runtipi/runtipi/security/advisories/GHSA-wcrf-g9p9-2wg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-55168
- https://github.com/runtipi/runtipi/commit/df529a211b05f3a0007b209b6c337f8c1942619c
- https://github.com/runtipi/runtipi/pull/2606
