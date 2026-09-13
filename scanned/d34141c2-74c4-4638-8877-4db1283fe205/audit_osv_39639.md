# [H] Manyfold: Authenticated Path Traversal via File Rename

## Summary
Severity: High
Advisory: CVE-2026-46336
Aliases: GHSA-j5f9-r7wf-hv37
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-46336
Type: osv

## Details
Manyfold is an open source, self-hosted web application for managing a collection of 3d models, particularly focused on 3d printing. From 0.96.0 until 0.140.0, authenticated users can rename uploaded files with path traversal sequences because app/models/model_file.rb uses the user-controlled filename in File.join(model.path, filename) without sufficient sanitization, allowing files to be moved or written outside the configured library directory. This issue is fixed in version 0.140.0.

## References
- https://github.com/manyfold3d/manyfold/releases/tag/v0.140.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46336.json
- https://github.com/manyfold3d/manyfold/security/advisories/GHSA-j5f9-r7wf-hv37
- https://nvd.nist.gov/vuln/detail/CVE-2026-46336
- https://github.com/manyfold3d/manyfold/commit/ed6a53e54926708594c07d222155ac3a22f93174
- https://github.com/manyfold3d/manyfold/pull/6122
