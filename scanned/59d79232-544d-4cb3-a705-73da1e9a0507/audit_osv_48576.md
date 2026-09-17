# [C] CVE-2017-9728

## Summary
Severity: Critical
Advisory: CVE-2017-9728
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2017-9728
Type: osv

## Details
In uClibc 0.9.33.2, there is an out-of-bounds read in the get_subexp function in misc/regex/regexec.c when processing a crafted regular expression.

## References
- http://openwall.com/lists/oss-security/2017/06/16/4
