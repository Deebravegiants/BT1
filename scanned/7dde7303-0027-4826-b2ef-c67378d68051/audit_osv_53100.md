# [H] CVE-2022-28736

## Summary
Severity: High
Advisory: CVE-2022-28736
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2022-28736
Type: osv

## Details
There's a use-after-free vulnerability in grub_cmd_chainloader() function; The chainloader command is used to boot up operating systems that doesn't support multiboot and do not have direct support from GRUB2. When executing chainloader more than once a use-after-free vulnerability is triggered. If an attacker can control the GRUB2's memory allocation pattern sensitive data may be exposed and arbitrary code execution can be achieved.

## References
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-28736
- https://security.netapp.com/advisory/ntap-20230825-0002/
- https://www.openwall.com/lists/oss-security/2022/06/07/5
