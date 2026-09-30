# [H] CVE-2017-6090

## Summary
Severity: High
Advisory: CVE-2017-6090
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-03
Source: https://osv.dev/vulnerability/CVE-2017-6090
Type: osv

## Details
Unrestricted file upload vulnerability in clients/editclient.php in PhpCollab 2.5.1 and earlier allows remote authenticated users to execute arbitrary code by uploading a file with an executable extension, then accessing it via a direct request to the file in logos_clients/.

## References
- https://sysdream.com/news/lab/2017-09-29-cve-2017-6090-phpcollab-2-5-1-arbitrary-file-upload-unauthenticated/
- https://www.exploit-db.com/exploits/42934/
- https://www.exploit-db.com/exploits/43519/
