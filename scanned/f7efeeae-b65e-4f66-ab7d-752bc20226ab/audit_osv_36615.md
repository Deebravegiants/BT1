# [C] RAGFlow Affected by Zip Slip Remote Code Execution (RCE) in MinerUParser

## Summary
Severity: Critical
Advisory: CVE-2026-24770
Aliases: GHSA-v7cf-w7gj-pgf4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24770
Type: osv

## Details
RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine. In version 0.23.1 and possibly earlier versions, the MinerU parser contains a "Zip Slip" vulnerability, allowing an attacker to overwrite arbitrary files on the server (leading to Remote Code Execution) via a malicious ZIP archive. The MinerUParser class retrieves and extracts ZIP files from an external source (mineru_server_url). The extraction logic in `_extract_zip_no_root` fails to sanitize filenames within the ZIP archive. Commit 64c75d558e4a17a4a48953b4c201526431d8338f contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24770.json
- https://github.com/infiniflow/ragflow/security/advisories/GHSA-v7cf-w7gj-pgf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-24770
- https://github.com/infiniflow/ragflow/commit/64c75d558e4a17a4a48953b4c201526431d8338f
