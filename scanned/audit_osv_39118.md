# [M] Path Traversal in build/packages/packages.toml Allows Arbitrary Directory Deletion

## Summary
Severity: Medium
Advisory: CVE-2026-43965
Aliases: EEF-CVE-2026-43965, GHSA-jqvf-f6p2-wrv3
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-43965
Type: osv

## Details
Path traversal vulnerability in Gleam's dependency management allows arbitrary directory deletion via malicious build/packages/packages.toml content.

Package keys read from build/packages/packages.toml by LocalPackages::read_from_disc are passed without validation to paths.build_packages_package(), which constructs a filesystem path by joining the project build directory with the attacker-controlled key. The resulting path is then passed to fs::delete_directory (which calls remove_dir_all). No check is performed to ensure the path remains within the intended build/packages/ directory. Both absolute paths and relative traversal sequences (e.g. ../) are accepted as package keys, allowing deletion of arbitrary directories.

An attacker who can cause a victim to run gleam deps download on a project containing a malicious build/packages/packages.toml (e.g. by committing the normally-gitignored file to a repository) can cause arbitrary directories on the victim's system to be recursively deleted.

This issue affects Gleam from 0.18.0-rc1 until 1.17.0.

## References
- https://cna.erlef.org/cves/CVE-2026-43965.html
- https://ghcr.io
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-43965
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43965.json
- https://github.com/gleam-lang/gleam/security/advisories/GHSA-jqvf-f6p2-wrv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-43965
- https://github.com/gleam-lang/gleam/commit/690ca069817bee5f77a28fc3e360627c1da19291
- https://github.com/gleam-lang/gleam
