# [M] CVE-2018-15536

## Summary
Severity: Medium
Advisory: CVE-2018-15536
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-08-24
Source: https://osv.dev/vulnerability/CVE-2018-15536
Type: osv

## Details
/filemanager/ajax_calls.php in tecrail Responsive FileManager before 9.13.4 does not properly validate file paths in archives, allowing for the extraction of crafted archives to overwrite arbitrary files via an extract action, aka Directory Traversal.

## References
- http://seclists.org/fulldisclosure/2018/Aug/34
- https://www.exploit-db.com/exploits/45271/
