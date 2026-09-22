# [H] CVE-2023-21106

## Summary
Severity: High
Advisory: CVE-2023-21106
Aliases: A-265016072, ASB-A-265016072
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-15
Source: https://osv.dev/vulnerability/CVE-2023-21106
Type: osv

## Details
In adreno_set_param of adreno_gpu.c, there is a possible memory corruption due to a double free. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-265016072References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2023-05-01
- https://source.android.com/security/bulletin/2023-05-01
