# [H] CVE-2023-21102

## Summary
Severity: High
Advisory: CVE-2023-21102
Aliases: A-260821414, ASB-A-260821414
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-15
Source: https://osv.dev/vulnerability/CVE-2023-21102
Type: osv

## Details
In __efi_rt_asm_wrapper of efi-rt-wrapper.S, there is a possible bypass of shadow stack protection due to a logic error in the code. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-260821414References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2023-05-01
- https://source.android.com/security/bulletin/2023-05-01
