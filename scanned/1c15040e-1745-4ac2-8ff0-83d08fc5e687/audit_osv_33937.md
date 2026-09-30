# [H] CVE-2025-52922

## Summary
Severity: High
Advisory: CVE-2025-52922
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2025-52922
Type: osv

## Details
Innoshop through 0.4.1 allows directory traversal via FileManager API endpoints. An authenticated attacker with access to the admin panel could abuse this to: (1) fully map the filesystem structure via the /api/file_manager/files?base_folder= endpoint, (2) create arbitrary directories on the server via the /api/file_manager/directories endpoint, (3) read arbitrary files from the server by copying the file to a readable location within the application via the /api/file_manager/copy_files endpoint, {4) delete arbitrary files from the server via a DELETE request to /api/file_manager/files, or (5) create arbitrary files on the server by uploading them and then leveraging the /api/file_manager/move_files endpoint to move them anywhere in the filesystem.

## References
- https://medium.com/@The_Hiker/how-i-found-multiple-cves-in-innoshop-0-4-1-12c8f84ad87f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52922.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52922
- https://github.com/innocommerce/innoshop
