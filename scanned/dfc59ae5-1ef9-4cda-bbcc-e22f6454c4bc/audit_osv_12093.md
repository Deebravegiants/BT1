# [M] CVE-2018-10186

## Summary
Severity: Medium
Advisory: CVE-2018-10186
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-17
Source: https://osv.dev/vulnerability/CVE-2018-10186
Type: osv

## Details
In radare2 2.5.0, there is a heap-based buffer over-read in the r_hex_bin2str function (libr/util/hex.c). Remote attackers could leverage this vulnerability to cause a denial of service via a crafted DEX file. This issue is different from CVE-2017-15368.

## References
- https://github.com/radare/radare2/issues/9915
