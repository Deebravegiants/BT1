# [H] drm/xe: Add bounds check on pat_index to prevent OOB kernel read in madvise

## Summary
Severity: High
Advisory: CVE-2026-43280
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43280
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Add bounds check on pat_index to prevent OOB kernel read in madvise

When user provides a bogus pat_index value through the madvise IOCTL, the
xe_pat_index_get_coh_mode() function performs an array access without
validating bounds. This allows a malicious user to trigger an out-of-bounds
kernel read from the xe->pat.table array.

The vulnerability exists because the validation in madvise_args_are_sane()
directly calls xe_pat_index_get_coh_mode(xe, args->pat_index.val) without
first checking if pat_index is within [0, xe->pat.n_entries).

Although xe_pat_index_get_coh_mode() has a WARN_ON to catch this in debug
builds, it still performs the unsafe array access in production kernels.

v2(Matthew Auld)
- Using array_index_nospec() to mitigate spectre attacks when the value
is used

v3(Matthew Auld)
- Put the declarations at the start of the block

(cherry picked from commit 944a3329b05510d55c69c2ef455136e2fc02de29)

## References
- https://git.kernel.org/stable/c/79f52655567a6471ff3d0d6325ede91bb14461f4
- https://git.kernel.org/stable/c/fbbe32618e97eff81577a01eb7d9adcd64a216d7
- https://git.kernel.org/stable/c/ffba51100ff61792fefbae11ca38ac1987a818dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43280.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
