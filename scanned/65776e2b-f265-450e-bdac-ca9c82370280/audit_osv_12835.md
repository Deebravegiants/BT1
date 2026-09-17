# [H] CVE-2018-15535

## Summary
Severity: High
Advisory: CVE-2018-15535
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-24
Source: https://osv.dev/vulnerability/CVE-2018-15535
Type: osv

## Details
/filemanager/ajax_calls.php in tecrail Responsive FileManager before 9.13.4 uses external input to construct a pathname that should be within a restricted directory, but it does not properly neutralize get_file sequences such as ".." that can resolve to a location that is outside of that directory, aka Directory Traversal.

## References
- http://seclists.org/fulldisclosure/2018/Aug/34
- https://www.exploit-db.com/exploits/45271/
