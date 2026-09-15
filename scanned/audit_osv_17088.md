# [H] CVE-2020-12103

## Summary
Severity: High
Advisory: CVE-2020-12103
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2020-04-28
Source: https://osv.dev/vulnerability/CVE-2020-12103
Type: osv

## Details
In Tiny File Manager 2.4.1 there is a vulnerability in the ajax file backup copy functionality which allows authenticated users to create backup copies of files (with .bak extension) outside the scope in the same directory in which they are stored.

## References
- https://cyberaz0r.info/2020/04/tiny-file-manager-multiple-vulnerabilities/
- https://github.com/prasathmani/tinyfilemanager/issues/357
- https://github.com/prasathmani/tinyfilemanager/commit/a0c595a8e11e55a43eeaa68e1a3ce76365f29d06
