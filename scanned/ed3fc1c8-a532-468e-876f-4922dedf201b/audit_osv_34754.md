# [H] pdfminer.six vulnerable to Arbitrary Code Execution via Crafted PDF Input

## Summary
Severity: High
Advisory: CVE-2025-64512
Aliases: GHSA-wf5f-4jwr-ppcp, PYSEC-2026-1762
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-11-10
Source: https://osv.dev/vulnerability/CVE-2025-64512
Type: osv

## Details
Pdfminer.six is a community maintained fork of the original PDFMiner, a tool for extracting information from PDF documents. Prior to version 20251107, pdfminer.six will execute arbitrary code from a malicious pickle file if provided with a malicious PDF file. The `CMapDB._load_data()` function in pdfminer.six uses `pickle.loads()` to deserialize pickle files. These pickle files are supposed to be part of the pdfminer.six distribution stored in the `cmap/` directory, but a malicious PDF can specify an alternative directory and filename as long as the filename ends in `.pickle.gz`. A malicious, zipped pickle file can then contain code which will automatically execute when the PDF is processed. Version 20251107 fixes the issue.

## References
- https://github.com/pdfminer/pdfminer.six/releases/tag/20251107
- https://lists.debian.org/debian-lts-announce/2025/11/msg00017.html
- https://lists.debian.org/debian-lts-announce/2026/01/msg00005.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64512.json
- https://github.com/pdfminer/pdfminer.six/security/advisories/GHSA-wf5f-4jwr-ppcp
- https://nvd.nist.gov/vuln/detail/CVE-2025-64512
- https://github.com/pdfminer/pdfminer.six/commit/b808ee05dd7f0c8ea8ec34bdf394d40e63501086
