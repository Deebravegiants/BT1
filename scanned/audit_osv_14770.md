# [H] CVE-2019-11377

## Summary
Severity: High
Advisory: CVE-2019-11377
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-20
Source: https://osv.dev/vulnerability/CVE-2019-11377
Type: osv

## Details
wcms/wex/finder/action.php in WCMS v0.3.2 has a Arbitrary File Upload Vulnerability via developer/finder because .php is a valid extension according to the fm_get_text_exts function.

## References
- http://www.iwantacve.cn/index.php/archives/208/
- https://github.com/vedees/wcms/issues/2
