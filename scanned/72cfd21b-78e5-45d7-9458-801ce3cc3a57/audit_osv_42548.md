# [H] firmware: arm_ffa: Fix Endpoint Memory Access Descriptor offset calculation

## Summary
Severity: High
Advisory: CVE-2026-68400
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68400
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_ffa: Fix Endpoint Memory Access Descriptor offset calculation

Use the descriptor's `ep_mem_offset` to calculate the start of the endpoint
memory access array and to comply with the FF-A spec instead of defaulting
to `sizeof(struct ffa_mem_region)`.
This requires moving `ffa_mem_region_additional_setup()` earlier in the setup
flow.
Also, add sanity checks to ensure the calculated descriptor offsets do not
exceed `max_fragsize`.

## References
- https://git.kernel.org/stable/c/8ef18f0ab3c0ec1eac77289f5a542bd96a8a6d66
- https://git.kernel.org/stable/c/b39b08e6bee812514b449dc874076890e6b871a0
- https://git.kernel.org/stable/c/b4d961351aa84fdf0148783fb1f3a1391b8a0adb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68400.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68400
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
