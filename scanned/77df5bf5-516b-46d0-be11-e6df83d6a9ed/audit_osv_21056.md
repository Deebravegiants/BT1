# [H] CVE-2021-4021

## Summary
Severity: High
Advisory: CVE-2021-4021
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/CVE-2021-4021
Type: osv

## Details
A vulnerability was found in Radare2 in versions prior to 5.6.2, 5.6.0, 5.5.4 and 5.5.2. Mapping a huge section filled with zeros of an ELF64 binary for MIPS architecture can lead to uncontrolled resource consumption and DoS.

## References
- https://github.com/radareorg/radare2/issues/19436
