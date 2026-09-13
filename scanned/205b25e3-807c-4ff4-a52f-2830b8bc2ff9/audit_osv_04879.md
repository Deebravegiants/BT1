# [H] Git allows arbitrary code execution through broken config quoting

## Summary
Severity: High
Advisory: BIT-git-2025-48384
Aliases: CVE-2025-48384, GHSA-vwqx-4fm8-6qc9
Ecosystem: Bitnami
Published: 2025-07-10
Source: https://osv.dev/vulnerability/BIT-git-2025-48384
Type: osv

## Affected
- Bitnami: `git` — affected >=0 <2.50.1

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. When reading a config value, Git strips any trailing carriage return and line feed (CRLF). When writing a config entry, values with a trailing CR are not quoted, causing the CR to be lost when the config is later read. When initializing a submodule, if the submodule path contains a trailing CR, the altered path is read resulting in the submodule being checked out to an incorrect location. If a symlink exists that points the altered path to the submodule hooks directory, and the submodule contains an executable post-checkout hook, the script may be unintentionally executed after checkout. This vulnerability is fixed in v2.43.7, v2.44.4, v2.45.4, v2.46.4, v2.47.3, v2.48.2, v2.49.1, and v2.50.1.

## References
- https://github.com/git/git/security/advisories/GHSA-vwqx-4fm8-6qc9
- https://nvd.nist.gov/vuln/detail/CVE-2025-48384
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-48384
- http://seclists.org/fulldisclosure/2025/Sep/60
- http://www.openwall.com/lists/oss-security/2025/07/08/4
- https://lists.debian.org/debian-lts-announce/2025/10/msg00003.html
