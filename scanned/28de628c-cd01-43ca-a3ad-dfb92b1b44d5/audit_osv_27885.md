# [H] drm/amd/display: Fix array-index-out-of-bounds in dcn35_clkmgr

## Summary
Severity: High
Advisory: CVE-2024-26699
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26699
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix array-index-out-of-bounds in dcn35_clkmgr

[Why]
There is a potential memory access violation while
iterating through array of dcn35 clks.

[How]
Limit iteration per array size.

## References
- https://git.kernel.org/stable/c/46806e59a87790760870d216f54951a5b4d545bc
- https://git.kernel.org/stable/c/ca400d8e0c1c9d79c08dfb6b7f966e26c8cae7fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26699.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26699
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
