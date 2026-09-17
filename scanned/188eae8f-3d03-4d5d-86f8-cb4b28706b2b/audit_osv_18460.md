# [H] CVE-2020-27795

## Summary
Severity: High
Advisory: CVE-2020-27795
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-19
Source: https://osv.dev/vulnerability/CVE-2020-27795
Type: osv

## Details
A segmentation fault was discovered in radare2 with adf command. In libr/core/cmd_anal.c, when command "adf" has no or wrong argument, anal_fcn_data (core, input + 1) --> RAnalFunction *fcn = r_anal_get_fcn_in (core->anal, core->offset, -1); returns null pointer for fcn causing segmentation fault later in ensure_fcn_range (fcn).

## References
- https://github.com/radareorg/radare2/commit/4d3811681a80f92a53e795f6a64c4b0fc2c8dd22
- https://github.com/radareorg/radare2/issues/16215
- https://github.com/radareorg/radare2/pull/16230
