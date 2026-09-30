# [M] CVE-2018-1000117

## Summary
Severity: Medium
Advisory: CVE-2018-1000117
Aliases: PSF-2022-2
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-07
Source: https://osv.dev/vulnerability/CVE-2018-1000117
Type: osv

## Details
Python Software Foundation CPython version From 3.2 until 3.6.4 on Windows contains a Buffer Overflow vulnerability in os.symlink() function on Windows that can result in Arbitrary code execution, likely escalation of privilege. This attack appears to be exploitable via a python script that creates a symlink with an attacker controlled name or location. This vulnerability appears to have been fixed in 3.7.0 and 3.6.5.

## References
- https://bugs.python.org/issue33001
- https://github.com/python/cpython/pull/5989
