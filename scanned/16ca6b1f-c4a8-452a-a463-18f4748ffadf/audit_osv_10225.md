# [C] CVE-2017-14402

## Summary
Severity: Critical
Advisory: CVE-2017-14402
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-13
Source: https://osv.dev/vulnerability/CVE-2017-14402
Type: osv

## Details
The EyesOfNetwork web interface (aka eonweb) 5.1-0 has SQL injection via the user_name parameter to module/admin_user/add_modify_user.php in the "ACCOUNT CREATION" section, related to lack of input validation in include/function.php.

## References
- http://www.sstrunk.com/cve/eonweb_include_function.html
