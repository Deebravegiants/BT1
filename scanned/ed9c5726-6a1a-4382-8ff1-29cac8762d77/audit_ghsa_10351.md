# [M] nbconvert has an Arbitrary File Write via Path Traversal in Cell Attachment Filenames

## Summary
Severity: Medium
Advisory: GHSA-4c99-qj7h-p3vg
CVE: CVE-2026-39377
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-4c99-qj7h-p3vg
Type: github-advisory

## Affected
- PyPI: `nbconvert` — affected >=6.5.0 <7.17.1

## Details
# Arbitrary File Write via Path Traversal in Cell Attachment Filenames

## Summary

nbconvert allows arbitrary file writes to locations outside the intended output directory when processing notebooks containing crafted cell attachment filenames. The `ExtractAttachmentsPreprocessor` passes attachment filenames directly to the filesystem without sanitization, enabling path traversal attacks. This vulnerability provides complete control over both the destination path and file extension.


## Impact

This vulnerability allows writing files with arbitrary content to arbitrary filesystem locations, limited only by the permissions of the process running nbconvert. The attacker controls:
- Full destination path (via `../` traversal)
- Filename
- File extension
- File content

## Patches

- upgrade to nbconvert v7.17.1

## Workarounds

disable ExtractAttachmentsPreprocessor by setting:

```python
c. ExtractAttachmentsPreprocessor.enabled = False
```

## References
- https://github.com/jupyter/nbconvert/security/advisories/GHSA-4c99-qj7h-p3vg
- https://nvd.nist.gov/vuln/detail/CVE-2026-39377
- https://github.com/jupyter/nbconvert
- https://github.com/jupyter/nbconvert/releases/tag/v7.17.1
