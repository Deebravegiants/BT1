# [H] drm/amd/display: Skip on writeback when it's not applicable

## Summary
Severity: High
Advisory: CVE-2024-36914
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36914
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.116, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Skip on writeback when it's not applicable

[WHY]
dynamic memory safety error detector (KASAN) catches and generates error
messages "BUG: KASAN: slab-out-of-bounds" as writeback connector does not
support certain features which are not initialized.

[HOW]
Skip them when connector type is DRM_MODE_CONNECTOR_WRITEBACK.

## References
- https://git.kernel.org/stable/c/87de0a741ef6d93fcb99983138a0d89a546a043c
- https://git.kernel.org/stable/c/951a498fa993c5501994ec2df97c9297b02488c7
- https://git.kernel.org/stable/c/e9baa7110e9f3756bd5a812af376c288d9be894d
- https://git.kernel.org/stable/c/ecedd99a9369fb5cde601ae9abd58bca2739f1ae
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36914.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36914
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
