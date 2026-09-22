# [M] CVE-2018-8964

## Summary
Severity: Medium
Advisory: CVE-2018-8964
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-23
Source: https://osv.dev/vulnerability/CVE-2018-8964
Type: osv

## Details
In libming 0.4.8, the decompileDELETE function of decompile.c has a use-after-free. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted swf file.

## References
- https://github.com/libming/libming/issues/130
