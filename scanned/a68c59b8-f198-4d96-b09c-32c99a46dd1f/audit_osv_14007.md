# [C] CVE-2018-6345

## Summary
Severity: Critical
Advisory: CVE-2018-6345
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2018-6345
Type: osv

## Details
The function number_format is vulnerable to a heap overflow issue when its second argument ($dec_points) is excessively large. The internal implementation of the function will cause a string to be created with an invalid length, which can then interact poorly with other functions. This affects all supported versions of HHVM (3.30.1 and 3.27.5 and below).

## References
- https://hhvm.com/blog/2019/01/14/hhvm-3.30.2.html
- https://github.com/facebook/hhvm/commit/190ffdf6c8b1ec443be202c7d69e63a7e3da25e3
