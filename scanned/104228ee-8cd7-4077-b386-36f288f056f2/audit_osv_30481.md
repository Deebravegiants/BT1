# [M] drm/amdgpu: prevent NULL pointer dereference if ATIF is not supported

## Summary
Severity: Medium
Advisory: CVE-2024-53060
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53060
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.323 <4.19.324, >=5.4.285 <5.4.286, >=5.10.229 <5.10.230, >=5.15.170 <5.15.172, >=6.1.115 <6.1.117, >=6.6.59 <6.6.61, >=6.11.6 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: prevent NULL pointer dereference if ATIF is not supported

acpi_evaluate_object() may return AE_NOT_FOUND (failure), which
would result in dereferencing buffer.pointer (obj) while being NULL.

Although this case may be unrealistic for the current code, it is
still better to protect against possible bugs.

Bail out also when status is AE_NOT_FOUND.

This fixes 1 FORWARD_NULL issue reported by Coverity
Report: CID 1600951:  Null pointer dereferences  (FORWARD_NULL)

(cherry picked from commit 91c9e221fe2553edf2db71627d8453f083de87a1)

## References
- https://git.kernel.org/stable/c/1a9f55ed5b512f510ccd21ad527d532e60550e80
- https://git.kernel.org/stable/c/27fc29b5376998c126c85cf9b15d9dfc2afc9cbe
- https://git.kernel.org/stable/c/2ac7f253deada4d449559b65a1c1cd0a6f6f19b7
- https://git.kernel.org/stable/c/8d7a28eca7553d35d4ce192fa1f390f2357df41b
- https://git.kernel.org/stable/c/a613a392417532ca5aaf3deac6e3277aa7aaef2b
- https://git.kernel.org/stable/c/a6dd15981c03f2cdc9a351a278f09b5479d53d2e
- https://git.kernel.org/stable/c/b9d9881237afeb52eddd70077b7174bf17e2fa30
- https://git.kernel.org/stable/c/ce8a00a00e36f61f5a1e47734332420b68784c43
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53060.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53060
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
