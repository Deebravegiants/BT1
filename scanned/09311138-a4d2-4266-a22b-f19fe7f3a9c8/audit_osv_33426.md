# [H] drm/gpusvm: fix hmm_pfn_to_map_order() usage

## Summary
Severity: High
Advisory: CVE-2025-40336
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-40336
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/gpusvm: fix hmm_pfn_to_map_order() usage

Handle the case where the hmm range partially covers a huge page (like
2M), otherwise we can potentially end up doing something nasty like
mapping memory which is outside the range, and maybe not even mapped by
the mm. Fix is based on the xe userptr code, which in a future patch
will directly use gpusvm, so needs alignment here.

v2:
  - Add kernel-doc (Matt B)
  - s/fls/ilog2/ (Thomas)

## References
- https://git.kernel.org/stable/c/08e9fd78ba1b9e95141181c69cc51795c9888157
- https://git.kernel.org/stable/c/c50729c68aaf93611c855752b00e49ce1fdd1558
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40336.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40336
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
