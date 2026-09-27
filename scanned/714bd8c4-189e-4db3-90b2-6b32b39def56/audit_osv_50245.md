# [H] CVE-2020-0041

## Summary
Severity: High
Advisory: CVE-2020-0041
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/CVE-2020-0041
Type: osv

## Details
In binder_transaction of binder.c, there is a possible out of bounds write due to an incorrect bounds check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-145988638References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2020-03-01
