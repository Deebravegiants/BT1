# [C] CVE-2016-3957

## Summary
Severity: Critical
Advisory: CVE-2016-3957
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2016-3957
Type: osv

## Details
The secure_load function in gluon/utils.py in web2py before 2.14.2 uses pickle.loads to deserialize session information stored in cookies, which might allow remote attackers to execute arbitrary code by leveraging knowledge of encryption_key.

## References
- https://usn.ubuntu.com/4030-1/
- https://github.com/web2py/web2py/blob/R-2.14.1/gluon/utils.py#L200
- https://devco.re/blog/2017/01/03/web2py-unserialize-code-execution-CVE-2016-3957/
