# [M] CVE-2018-20461

## Summary
Severity: Medium
Advisory: CVE-2018-20461
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-25
Source: https://osv.dev/vulnerability/CVE-2018-20461
Type: osv

## Details
In radare2 prior to 3.1.1, core_anal_bytes in libr/core/cmd_anal.c allows attackers to cause a denial-of-service (application crash caused by out-of-bounds read) by crafting a binary file.

## References
- https://github.com/radare/radare2/commit/a1bc65c3db593530775823d6d7506a457ed95267
- https://github.com/radare/radare2/issues/12375
