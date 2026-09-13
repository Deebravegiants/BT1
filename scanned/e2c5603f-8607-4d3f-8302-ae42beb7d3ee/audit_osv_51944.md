# [H] CVE-2021-45972

## Summary
Severity: High
Advisory: CVE-2021-45972
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45972
Type: osv

## Details
The giftrans function in giftrans 1.12.2 contains a stack-based buffer overflow because a value inside the input file determines the amount of data to write. This allows an attacker to overwrite up to 250 bytes outside of the allocated buffer with arbitrary data.

## References
- https://www.abdn.ac.uk/tools/ibmpc/giftrans/index.hti
- http://web.archive.org/web/20150801185019/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1002739
