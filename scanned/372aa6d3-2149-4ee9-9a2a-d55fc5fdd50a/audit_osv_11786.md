# [H] CVE-2017-9750

## Summary
Severity: High
Advisory: CVE-2017-9750
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-9750
Type: osv

## Details
opcodes/rx-decode.opc in GNU Binutils 2.28 lacks bounds checks for certain scale arrays, which allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted binary file, as demonstrated by mishandling of this file during "objdump -D" execution.

## References
- https://www.exploit-db.com/exploits/42198/
- http://www.securityfocus.com/bid/99118
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=21587
