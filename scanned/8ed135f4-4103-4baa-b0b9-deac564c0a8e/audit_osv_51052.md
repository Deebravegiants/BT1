# [M] CVE-2021-0938

## Summary
Severity: Medium
Advisory: CVE-2021-0938
Aliases: A-171418586, PUB-A-171418586
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-0938
Type: osv

## Details
In memzero_explicit of compiler-clang.h, there is a possible bypass of defense in depth due to uninitialized data. This could lead to local information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-171418586References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2021-10-01
