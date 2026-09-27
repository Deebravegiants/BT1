# [H] CVE-2020-12851

## Summary
Severity: High
Advisory: CVE-2020-12851
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/CVE-2020-12851
Type: osv

## Details
Pydio Cells 2.0.4 allows an authenticated user to write or overwrite existing files in another user’s personal and cells folders (repositories) by uploading a custom generated ZIP file and leveraging the file extraction feature present in the web application. The extracted files will be placed in the targeted user folders.

## References
- http://packetstormsecurity.com/files/158002/Pydio-Cells-2.0.4-XSS-File-Write-Code-Execution.html
- https://www.coresecurity.com/advisories
- https://www.coresecurity.com/core-labs/advisories/pydio-cells-204-multiple-vulnerabilities
