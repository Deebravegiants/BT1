# [H] CVE-2025-51661

## Summary
Severity: High
Advisory: CVE-2025-51661
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-51661
Type: osv

## Details
A path Traversal vulnerability found in FileCodeBox v2.2 and earlier allows arbitrary file writes when application is configured to use local filesystem storage. SystemFileStorage.save_file method in core/storage.py uses filenames from user input without validation to construct save_path and save files. This allows remote attackers to perform arbitrary file writes outside the intended directory by sending crafted POST requests with malicious traversal sequences to /share/file/ upload endpoint, which does not require any authorization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51661.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51661
- https://github.com/vastsa/FileCodeBox/issues/349
- https://github.com/vastsa/FileCodeBox
