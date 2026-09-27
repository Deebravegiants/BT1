# [H] drm/amd/display: populate subvp cmd info only for the top pipe

## Summary
Severity: High
Advisory: CVE-2023-53806
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53806
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: populate subvp cmd info only for the top pipe

[Why]
System restart observed while changing the display resolution
to 8k with extended mode. Sytem restart was caused by a page fault.

[How]
When the driver populates subvp info it did it for both the pipes using
vblank which caused an outof bounds array access causing the page fault.
added checks to allow the top pipe only to fix this issue.

## References
- https://git.kernel.org/stable/c/375d192eb1f1d9229a6d994da7ba31f3582b106b
- https://git.kernel.org/stable/c/92e6c79acad4b96efeff261d27bdbd8089a7dd24
- https://git.kernel.org/stable/c/9bb10b7aaec3b6278f9cc410c17dcaa129bbbbf0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53806.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53806
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
