# [M] Improper Path Validation in Git Dependency Handling Allows Arbitrary File System Modification

## Summary
Severity: Medium
Advisory: CVE-2026-32146
Aliases: EEF-CVE-2026-32146, GHSA-vq5j-55vx-wq8j
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2026-04-11
Source: https://osv.dev/vulnerability/CVE-2026-32146
Type: osv

## Details
Improper path validation vulnerability in the Gleam compiler's handling of git dependencies allows arbitrary file system modification during dependency download.

Dependency names from gleam.toml and manifest.toml are incorporated into filesystem paths without sufficient validation or confinement to the intended dependency directory, allowing attacker-controlled paths (via relative traversal such as ../ or absolute paths) to target filesystem locations outside that directory. When resolving git dependencies (e.g. via gleam deps download), the computed path is used for filesystem operations including directory deletion and creation.

This vulnerability occurs during the dependency resolution and download phase, which is generally expected to be limited to fetching and preparing dependencies within a confined directory. A malicious direct or transitive git dependency can exploit this issue to delete and overwrite arbitrary directories outside the intended dependency directory, including attacker-chosen absolute paths, potentially causing data loss. In some environments, this may be further leveraged to achieve code execution, for example by overwriting git hooks or shell configuration files.

This issue affects Gleam from 1.9.0-rc1 until 1.15.4.

## References
- https://cna.erlef.org/cves/CVE-2026-32146.html
- https://ghcr.io
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-32146
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32146.json
- https://access.redhat.com/security/cve/CVE-2026-32146
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32146.json
- https://github.com/gleam-lang/gleam/security/advisories/GHSA-vq5j-55vx-wq8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-32146
- https://bugzilla.redhat.com/show_bug.cgi?id=2457578
- https://github.com/gleam-lang/gleam/commit/1aa5d8e594b0aa240bb213fce6ee19c65e6d5bcf
- https://github.com/gleam-lang/gleam/commit/2dc0467f822c75de94697a912755d172928ee40a
- https://github.com/gleam-lang/gleam
