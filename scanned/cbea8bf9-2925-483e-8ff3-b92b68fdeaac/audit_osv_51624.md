# [H] CVE-2021-3624

## Summary
Severity: High
Advisory: CVE-2021-3624
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2021-3624
Type: osv

## Details
There is an integer overflow vulnerability in dcraw. When the victim runs dcraw with a maliciously crafted X3F input image, arbitrary code may be executed in the victim's system.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=984761
