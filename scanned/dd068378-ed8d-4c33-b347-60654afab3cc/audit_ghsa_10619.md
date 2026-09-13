# [M] Junrar: Path Traversal (Zip-Slip) via Sibling Directory Name Prefix

## Summary
Severity: Medium
Advisory: GHSA-hf5p-q87m-crj7
CVE: CVE-2026-41245
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-hf5p-q87m-crj7
Type: github-advisory

## Affected
- Maven: `com.github.junrar:junrar` — affected >=0 <7.5.10

## Details
### Summary

A path traversal vulnerability in `LocalFolderExtractor` allows an attacker to write arbitrary files with attacker-controlled content into sibling directories when a crafted RAR archive is extracted.

### Example

Given an extraction directory set to `/tmp/extract`, a crafted archive with an entry with the filename as `../extract_evil/file.txt` would be actually extracted to `/tmp/extract_evil/file.txt`.

### Details

The `createDirectory()` and `createFile()` methods in`LocalFolderExtractor` validate extraction paths using a string prefix.

## References
- https://github.com/junrar/junrar/security/advisories/GHSA-hf5p-q87m-crj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-41245
- https://github.com/junrar/junrar/commit/d77e9a83eb721cd51f9c23d7869d0e6ad7f952d7
- https://github.com/junrar/junrar
- https://github.com/junrar/junrar/releases/tag/v7.5.10
