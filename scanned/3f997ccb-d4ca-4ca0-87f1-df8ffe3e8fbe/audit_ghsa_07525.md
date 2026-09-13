# [C] Home Assistant Core vulnerable to Path Traversal via backup upload during onboarding

## Summary
Severity: Critical
Advisory: GHSA-5hxg-r395-fqxx
CVE: CVE-2026-64825
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-5hxg-r395-fqxx
Type: github-advisory

## Affected
- PyPI: `homeassistant` — affected >=0 <2026.6.0

## Details
Home Assistant Core before 2026.6.0 contains a path traversal vulnerability that allows unauthenticated attackers to write arbitrary files to any directory on the host filesystem by uploading a crafted backup archive during the initial onboarding window. Attackers can manipulate the 'name' field inside the uploaded archive's backup.json to supply an absolute path, causing pathlib.Path.__truediv__ to discard the configured backup directory prefix and write attacker-controlled content to arbitrary locations, with full filesystem access when the process runs as root.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-64825
- https://github.com/home-assistant/core/pull/172368
- https://github.com/home-assistant/core/commit/567fe858289876b68b8162a77bd46e1e1af79752
- https://github.com/home-assistant/core
- https://github.com/home-assistant/core/releases/tag/2026.6.0
- https://www.vulncheck.com/advisories/home-assistant-core-path-traversal-file-write-via-backup-upload
