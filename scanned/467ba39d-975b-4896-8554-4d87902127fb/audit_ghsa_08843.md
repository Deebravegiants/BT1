# [M] Rust OneNote File Parser: Path traversal in `Parser::parse_notebook` allows reading files outside the notebook directory

## Summary
Severity: Medium
Advisory: GHSA-4j5m-wc25-pvh7
CVE: CVE-2026-46671
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-4j5m-wc25-pvh7
Type: github-advisory

## Affected
- crates.io: `onenote_parser` — affected >=0 <1.1.1

## Details
### Impact
A maliciously crafted `.onetoc2` table-of-contents file can cause `Parser::parse_notebook` to open arbitrary files on the host filesystem outside the notebook's directory. The parser reads entry names listed inside the `.onetoc2` and joins them against the notebook's base directory without validating that they are relative paths confined to that directory.

The parser will bail out when the target file fails to parse as a OneNote section, so direct content exfiltration through the parser's return value is not practical, though file-existence probing and denial-of-service via large or special files remain possible.

Anyone using `onenote_parser` to parse .onetoc2 files received from untrusted sources is affected. Users who only ever parse their own notebooks are not at meaningful risk.

### Patches
Fixed in onenote_parser 1.1.1. The fix rejects absolute paths, parent-directory components, and other invalid path characters in entry names, and additionally canonicalises the resolved path to confirm it stays inside the notebook's base directory.

### Workarounds
For users who cannot upgrade to 1.1.1:

- Only call `Parser::parse_notebook` on `.onetoc2` files from trusted sources.
- Alternatively, use `Parser::parse_section` / `Parser::parse_section_buffer` on individual .one files, which do not perform the directory walk.

## References
- https://github.com/msiemens/onenote.rs/security/advisories/GHSA-4j5m-wc25-pvh7
- https://github.com/msiemens/onenote.rs/commit/c9267b2c96e2542be7e7b557d67318e81b733585
- https://github.com/msiemens/onenote.rs
- https://github.com/msiemens/onenote.rs/blob/master/CHANGELOG.md#111---2026-05-15
- https://github.com/msiemens/onenote.rs/releases/tag/v1.1.1
