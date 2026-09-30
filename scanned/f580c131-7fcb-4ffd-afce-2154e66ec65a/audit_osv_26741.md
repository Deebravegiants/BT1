# [H] drm/amd/display: fix mapping to non-allocated address

## Summary
Severity: High
Advisory: CVE-2023-53753
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2023-53753
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: fix mapping to non-allocated address

[Why]
There is an issue mapping non-allocated location of memory.
It would allocate gpio registers from an array out of bounds.

[How]
Patch correct numbers of bounds for using.

## References
- https://git.kernel.org/stable/c/24aaf6603600d6d1159973c809ea2737664b28c4
- https://git.kernel.org/stable/c/8ce8a443ddd9002861a4ee8a7e33a0c02717422f
- https://git.kernel.org/stable/c/9190d4a263264eabf715f5fc1827da45e3fdc247
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53753.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53753
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
