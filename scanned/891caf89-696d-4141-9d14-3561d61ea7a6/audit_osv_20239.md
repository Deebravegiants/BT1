# [C] CVE-2021-32495

## Summary
Severity: Critical
Advisory: CVE-2021-32495
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-07-07
Source: https://osv.dev/vulnerability/CVE-2021-32495
Type: osv

## Details
Radare2 has a use-after-free vulnerability in pyc parser's get_none_object function. Attacker can read freed memory afterwards. This will allow attackers to cause denial of service.

## References
- https://github.com/radareorg/radare2/commit/5e16e2d1c9fe245e4c17005d779fde91ec0b9c05
- https://github.com/radareorg/radare2/issues/18666
