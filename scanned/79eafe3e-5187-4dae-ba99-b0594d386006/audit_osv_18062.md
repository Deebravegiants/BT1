# [H] CVE-2020-23352

## Summary
Severity: High
Advisory: CVE-2020-23352
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-01-27
Source: https://osv.dev/vulnerability/CVE-2020-23352
Type: osv

## Details
Z-BlogPHP 1.6.0 Valyria is affected by incorrect access control. PHP loose comparison and a magic hash can be used to bypass authentication. zb_user/plugin/passwordvisit/include.php:passwordvisit_input_password() uses loose comparison to authenticate, which can be bypassed via magic hash values.

## References
- https://github.com/zblogcn/zblogphp/commit/a67607fc984f976d6b36b8870dffaabd9d6c9d5e
