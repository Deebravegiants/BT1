# [H] CVE-2023-20928

## Summary
Severity: High
Advisory: CVE-2023-20928
Aliases: A-254837884, ASB-A-254837884
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/CVE-2023-20928
Type: osv

## Details
In binder_vma_close of binder.c, there is a possible use after free due to improper locking. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-254837884References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2023-01-01
- http://packetstormsecurity.com/files/170855/Android-Binder-VMA-Management-Security-Issues.html
