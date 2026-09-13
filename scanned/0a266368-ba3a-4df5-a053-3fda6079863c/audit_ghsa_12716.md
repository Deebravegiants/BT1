# [M] Path traversal in ubi-reader

## Summary
Severity: Medium
Advisory: GHSA-vp2x-3mc3-3cj4
CVE: CVE-2023-0591
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-vp2x-3mc3-3cj4
Type: github-advisory

## Affected
- PyPI: `ubi-reader` — affected >=0 <0.8.5

## Details
ubireader_extract_files is vulnerable to path traversal when run against specifically crafted UBIFS files, allowing the attacker to overwrite files outside of the extraction directory (provided the process has write access to that file or directory). This is due to the fact that a node name (dent_node.name) is considered trusted and joined to the extraction directory path during processing, then the node content is written to that joined path. By crafting a malicious UBIFS file with node names holding path traversal payloads (e.g. ../../tmp/outside.txt), it's possible to force ubi_reader to write outside of the extraction directory. This issue affects ubi-reader before 0.8.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0591
- https://github.com/jrspruitt/ubi_reader/pull/57
- https://github.com/jrspruitt/ubi_reader/commit/d5d68e6b1b9f7070c29df5f67fc060f579ae9139
- https://github.com/jrspruitt/ubi_reader
- https://github.com/pypa/advisory-database/tree/main/vulns/ubi-reader/PYSEC-2023-51.yaml
- https://onekey.com/blog/security-advisory-remote-command-execution-in-binwalk
