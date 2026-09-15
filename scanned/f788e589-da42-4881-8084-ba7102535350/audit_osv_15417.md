# [H] CVE-2019-16113

## Summary
Severity: High
Advisory: CVE-2019-16113
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-08
Source: https://osv.dev/vulnerability/CVE-2019-16113
Type: osv

## Details
Bludit 3.9.2 allows remote code execution via bl-kernel/ajax/upload-images.php because PHP code can be entered with a .jpg file name, and then this PHP code can write other PHP code to a ../ pathname.

## References
- http://packetstormsecurity.com/files/155295/Bludit-Directory-Traversal-Image-File-Upload.html
- http://packetstormsecurity.com/files/157988/Bludit-3.9.12-Directory-Traversal.html
- http://packetstormsecurity.com/files/158569/Bludit-3.9.2-Directory-Traversal.html
- https://github.com/bludit/bludit/issues/1081
