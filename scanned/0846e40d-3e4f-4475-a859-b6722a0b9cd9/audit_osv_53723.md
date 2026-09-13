# [H] CVE-2023-20938

## Summary
Severity: High
Advisory: CVE-2023-20938
Aliases: A-257685302, ASB-A-257685302
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-20938
Type: osv

## Details
In binder_transaction_buffer_release of binder.c, there is a possible use after free due to improper input validation. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-257685302References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2023-02-01
- https://source.android.com/security/bulletin/2023-02-01
