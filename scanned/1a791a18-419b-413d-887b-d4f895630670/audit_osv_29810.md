# [H] drm/amd/display: Fix index may exceed array range within fpu_update_bw_bounding_box

## Summary
Severity: High
Advisory: CVE-2024-46811
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46811
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix index may exceed array range within fpu_update_bw_bounding_box

[Why]
Coverity reports OVERRUN warning. soc.num_states could
be 40. But array range of bw_params->clk_table.entries is 8.

[How]
Assert if soc.num_states greater than 8.

## References
- https://git.kernel.org/stable/c/188fd1616ec43033cedbe343b6579e9921e2d898
- https://git.kernel.org/stable/c/4003bac784380fed1f94f197350567eaa73a409d
- https://git.kernel.org/stable/c/aba188d6f4ebaf52acf13f204db2bd2c22072504
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46811.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46811
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
