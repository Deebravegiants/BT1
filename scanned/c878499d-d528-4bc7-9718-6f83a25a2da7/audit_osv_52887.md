# [M] CVE-2022-20166

## Summary
Severity: Medium
Advisory: CVE-2022-20166
Aliases: A-182388481, PUB-A-182388481
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-15
Source: https://osv.dev/vulnerability/CVE-2022-20166
Type: osv

## Details
In various methods of kernel base drivers, there is a possible out of bounds write due to a heap buffer overflow. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-182388481References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2022-06-01
- https://source.android.com/security/bulletin/pixel/2022-06-01
