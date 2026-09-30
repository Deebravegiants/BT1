# [H] CVE-2018-7869

## Summary
Severity: High
Advisory: CVE-2018-7869
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-08
Source: https://osv.dev/vulnerability/CVE-2018-7869
Type: osv

## Details
There is a memory leak triggered in the function dcinit of util/decompile.c in libming 0.4.8, which will lead to a denial of service attack.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=892260
- https://github.com/libming/libming/issues/119
