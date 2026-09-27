# [H] Manyfold vulnerable to OS command injection via ZIP filename in f3d render

## Summary
Severity: High
Advisory: CVE-2026-27635
Aliases: GHSA-p589-cf26-v7h2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27635
Type: osv

## Details
Manyfold is an open source, self-hosted web application for managing a collection of 3d models, particularly focused on 3d printing. Prior to version 0.133.0, when model render generation is enabled, a logged-in user can achieve RCE by uploading a ZIP containing a file with a shell metacharacter in its name. The filename reaches a Ruby backtick call unsanitized. Version 0.133.0 fixes the issue.

## References
- https://github.com/manyfold3d/manyfold/releases/tag/v0.133.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27635.json
- https://github.com/manyfold3d/manyfold/security/advisories/GHSA-p589-cf26-v7h2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27635
