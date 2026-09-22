# [H] CVE-2017-9729

## Summary
Severity: High
Advisory: CVE-2017-9729
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2017-9729
Type: osv

## Details
In uClibc 0.9.33.2, there is stack exhaustion (uncontrolled recursion) in the check_dst_limits_calc_pos_1 function in misc/regex/regexec.c when processing a crafted regular expression.

## References
- http://openwall.com/lists/oss-security/2017/06/16/4
