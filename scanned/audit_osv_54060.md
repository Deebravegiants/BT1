# [M] CVE-2023-37732

## Summary
Severity: Medium
Advisory: CVE-2023-37732
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-26
Source: https://osv.dev/vulnerability/CVE-2023-37732
Type: osv

## Details
Yasm v1.3.0.78 was found prone to NULL Pointer Dereference in /libyasm/intnum.c and /elf/elf.c, which allows the attacker to cause a denial of service via a crafted file.

## References
- https://gist.github.com/ChanStormstout/02eea9cf5c002b42b2ff3de5ca939520
- https://github.com/yasm/yasm/issues/233
