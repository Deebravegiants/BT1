# [M] CVE-2019-12980

## Summary
Severity: Medium
Advisory: CVE-2019-12980
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-12980
Type: osv

## Details
In Ming (aka libming) 0.4.8, there is an integer overflow (caused by an out-of-range left shift) in the SWFInput_readSBits function in blocks/input.c. Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted swf file.

## References
- https://github.com/libming/libming/commit/a009a38dce1d9316cad1ab522b813b1d5ba4c62a
