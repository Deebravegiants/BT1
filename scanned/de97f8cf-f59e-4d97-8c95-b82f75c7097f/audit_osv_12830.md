# [H] CVE-2018-15495

## Summary
Severity: High
Advisory: CVE-2018-15495
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-18
Source: https://osv.dev/vulnerability/CVE-2018-15495
Type: osv

## Details
/filemanager/upload.php in Responsive FileManager before 9.13.3 allows Directory Traversal and SSRF because the url parameter is used directly in a curl_exec call, as demonstrated by a file:///etc/passwd value.

## References
- https://github.com/trippo/ResponsiveFilemanager/blob/master/changelog.txt
- http://seclists.org/fulldisclosure/2018/Aug/9
