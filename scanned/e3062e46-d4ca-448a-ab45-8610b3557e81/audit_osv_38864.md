# [M] Symlink Following in Hex Package Export Allows Embedding Files Outside Project Root

## Summary
Severity: Medium
Advisory: CVE-2026-42795
Aliases: EEF-CVE-2026-42795, GHSA-qhh5-fg4c-8gqc
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-42795
Type: osv

## Details
Symlink following vulnerability in Gleam's Hex package export allows files outside the project root to be embedded in the generated package tarball.

The file collection helpers (gleam_files, native_files, private_files) in compiler-cli/src/fs.rs use follow_links(true) when walking publishable directories such as src/ and priv/. The collected paths are added to the package archive via add_path_to_tar in compiler-cli/src/publish.rs without verifying that the resolved target remains within the project root. A symlink placed under a publishable directory will cause gleam export hex-tarball or gleam publish to embed the contents of the symlink target into the generated Hex package.

An attacker with write access to the project repository can place a symlink in src/ or priv/ pointing to an arbitrary file. When a maintainer or CI pipeline runs gleam publish or gleam export hex-tarball, local files readable by the publisher (such as secrets, tokens, or SSH keys) are silently embedded into the published package artifact.

This issue affects Gleam from 0.10.0-rc1 until 1.17.0.

## References
- https://cna.erlef.org/cves/CVE-2026-42795.html
- https://ghcr.io
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-42795
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42795.json
- https://github.com/gleam-lang/gleam/security/advisories/GHSA-qhh5-fg4c-8gqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42795
- https://github.com/gleam-lang/gleam/commit/6435a5528b9ae0449e2f32be579641ec485f6866
- https://github.com/gleam-lang/gleam
