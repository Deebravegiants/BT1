# [M] CVE-2018-20457

## Summary
Severity: Medium
Advisory: CVE-2018-20457
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-25
Source: https://osv.dev/vulnerability/CVE-2018-20457
Type: osv

## Details
In radare2 through 3.1.3, the assemble function inside libr/asm/p/asm_arm_cs.c allows attackers to cause a denial-of-service (application crash via an r_num_calc out-of-bounds read) by crafting an arm assembly input because a loop uses an incorrect index in armass.c and certain length validation is missing in armass64.c, a related issue to CVE-2018-20459.

## References
- https://github.com/radare/radare2/issues/12417
- https://github.com/radareorg/radare2/commit/e5c14c167b0dcf0a53d76bd50bacbbcc0dfc1ae7
