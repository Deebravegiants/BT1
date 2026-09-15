# [H] MoviePilot Path Traversal via Cloud Storage Download Handlers

## Summary
Severity: High
Advisory: CVE-2026-11416
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-11416
Type: osv

## Details
MoviePilot contains a path traversal vulnerability in the AliPan, U115, and Rclone cloud storage download handlers where the local destination path is constructed by concatenating the configured download directory with a filename taken directly from remote cloud API metadata without basename normalization or path validation. An attacker who controls a filename returned by a remote cloud storage API can include traversal sequences ../ in the filename to cause downloaded content to be written outside the configured download directory, potentially overwriting arbitrary files including configuration or plugin files reachable by the application process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11416.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11416
- https://github.com/jxxghp/MoviePilot/issues/5894
- https://github.com/jxxghp/MoviePilot/commit/a0b3800f6bf4857bf4f889a63d44350eb8380f28
- https://github.com/jxxghp/MoviePilot
