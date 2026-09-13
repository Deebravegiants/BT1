# [H] CVE-2024-29511

## Summary
Severity: High
Advisory: CVE-2024-29511
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-29511
Type: osv

## Details
Artifex Ghostscript before 10.03.1, when Tesseract is used for OCR, has a directory traversal issue that allows arbitrary file reading (and writing of error messages to arbitrary files) via OCRLanguage. For example, exploitation can use debug_file /tmp/out and user_patterns_file /etc/passwd.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=707510
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=3d4cfdc1a44
- https://www.openwall.com/lists/oss-security/2024/07/03/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29511.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29511
