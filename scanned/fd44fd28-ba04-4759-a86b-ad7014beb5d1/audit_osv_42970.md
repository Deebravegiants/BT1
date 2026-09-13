# [H] gpu/buddy: bail out of try_harder when alignment cannot be honoured

## Summary
Severity: High
Advisory: CVE-2026-72244
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72244
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpu/buddy: bail out of try_harder when alignment cannot be honoured

The try_harder contiguous fallback could return a range whose start
offset did not match the caller's min_block_size. When a candidate's
start is misaligned, realign it: free the misaligned run and reallocate
exactly @size at the next lower min_block_size boundary. This keeps the
returned size unchanged with no surplus to trim, and rejects the request
only when no aligned candidate fits.

v2: align misaligned candidates down to min_block_size instead of
    bailing out, for both the RHS and LHS paths (Matthew).

## References
- https://git.kernel.org/stable/c/419d7d9306491f3e0e417cf794844c73cabee090
- https://git.kernel.org/stable/c/4289531106ee175a6eb45db7d4f2734d1dae9887
- https://git.kernel.org/stable/c/56bc6384314fb9ae98975fb2af8b143097ede3dc
- https://git.kernel.org/stable/c/7185c5262435b93e5eeffa647008992256b9c51a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72244.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72244
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
