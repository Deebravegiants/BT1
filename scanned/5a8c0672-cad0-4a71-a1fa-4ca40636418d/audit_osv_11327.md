# [C] CVE-2017-7402

## Summary
Severity: Critical
Advisory: CVE-2017-7402
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2017-7402
Type: osv

## Details
Pixie 1.0.4 allows remote authenticated users to upload and execute arbitrary PHP code via the POST data in an admin/index.php?s=publish&x=filemanager request for a filename with a double extension, such as a .jpg.php file with Content-Type of image/jpeg.

## References
- https://www.exploit-db.com/exploits/41784/
- http://rungga.blogspot.co.id/2017/04/remote-file-upload-vulnerability-in.html
