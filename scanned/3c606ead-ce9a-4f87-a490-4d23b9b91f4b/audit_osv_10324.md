# [H] CVE-2017-14958

## Summary
Severity: High
Advisory: CVE-2017-14958
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-02
Source: https://osv.dev/vulnerability/CVE-2017-14958
Type: osv

## Details
lib.php in PivotX 2.3.11 does not properly block uploads of dangerous file types by admin users, which allows remote PHP code execution via an upload of a .php file.

## References
- https://sourceforge.net/p/pivot-weblog/code/4490/
