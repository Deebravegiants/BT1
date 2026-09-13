# [H] CVE-2016-3952

## Summary
Severity: High
Advisory: CVE-2016-3952
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2016-3952
Type: osv

## Details
web2py before 2.14.1, when using the standalone version, allows remote attackers to obtain environment variable values via a direct request to examples/template_examples/beautify.  NOTE: this issue can be leveraged by remote attackers to gain administrative access.

## References
- https://usn.ubuntu.com/4030-1/
- https://github.com/web2py/web2py/commit/9706d125b42481178d2b423de245f5d2faadbf40
- https://devco.re/blog/2017/01/03/web2py-unserialize-code-execution-CVE-2016-3957/
