# [H] Directory Traversal in stitionai/devika

## Summary
Severity: High
Advisory: CVE-2024-5547
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-5547
Type: osv

## Details
A directory traversal vulnerability exists in the /api/download-project-pdf endpoint of the stitionai/devika repository, affecting the latest version. The vulnerability arises due to insufficient sanitization of the 'project_name' parameter in the download_project_pdf function. Attackers can exploit this flaw by manipulating the 'project_name' parameter in a GET request to traverse the directory structure and download arbitrary PDF files from the system. This issue allows attackers to access sensitive information that could be stored in PDF format outside the intended directory.

## References
- https://huntr.com/bounties/7ea0eb5f-7643-4452-bc93-a225e2090283
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5547.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5547
- https://github.com/stitionai/devika/commit/6acce21fb08c3d1123ef05df6a33912bf0ee77c2
