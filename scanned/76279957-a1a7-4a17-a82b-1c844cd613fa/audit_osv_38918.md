# [C] ext4: handle wraparound when searching for blocks for indirect mapped blocks

## Summary
Severity: Critical
Advisory: CVE-2026-43067
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-43067
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.167 <6.1.168, >=6.6.130 <6.6.134, >=6.12.77 <6.12.80, >=6.18.14 <6.18.21, >=6.19.4 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: handle wraparound when searching for blocks for indirect mapped blocks

Commit 4865c768b563 ("ext4: always allocate blocks only from groups
inode can use") restricts what blocks will be allocated for indirect
block based files to block numbers that fit within 32-bit block
numbers.

However, when using a review bot running on the latest Gemini LLM to
check this commit when backporting into an LTS based kernel, it raised
this concern:

   If ac->ac_g_ex.fe_group is >= ngroups (for instance, if the goal
   group was populated via stream allocation from s_mb_last_groups),
   then start will be >= ngroups.

   Does this allow allocating blocks beyond the 32-bit limit for
   indirect block mapped files? The commit message mentions that
   ext4_mb_scan_groups_linear() takes care to not select unsupported
   groups. However, its loop uses group = *start, and the very first
   iteration will call ext4_mb_scan_group() with this unsupported
   group because next_linear_group() is only called at the end of the
   iteration.

After reviewing the code paths involved and considering the LLM
review, I determined that this can happen when there is a file system
where some files/directories are extent-mapped and others are
indirect-block mapped.  To address this, add a safety clamp in
ext4_mb_scan_groups().

## References
- https://git.kernel.org/stable/c/12624c5b724a81e14e532972b40d863b0de3b7d1
- https://git.kernel.org/stable/c/2a368ccddfc492a0aa951e2caef2985f20e96503
- https://git.kernel.org/stable/c/4bec4a498ce86314d470ae6144120461f2138c29
- https://git.kernel.org/stable/c/83170a05908b6cf2fb3235d3065bf613ff866f3c
- https://git.kernel.org/stable/c/bb81702370fad22c06ca12b6e1648754dbc37e0f
- https://git.kernel.org/stable/c/f89bba144938921a2249237ad04a0183ff3f8930
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43067.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43067
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
