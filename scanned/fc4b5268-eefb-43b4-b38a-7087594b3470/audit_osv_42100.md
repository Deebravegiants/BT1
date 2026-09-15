# [H] net/mlx5e: Fix eswitch mode block underflow on IPsec acquire SA

## Summary
Severity: High
Advisory: CVE-2026-64522
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64522
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Fix eswitch mode block underflow on IPsec acquire SA

mlx5e_xfrm_add_state() handles acquire-flow temporary SAs by allocating
software state and skipping hardware offload setup.

That path jumps to the common success label before taking the eswitch mode
block. After tunnel-mode validation was moved earlier, the common success
label unconditionally calls mlx5_eswitch_unblock_mode(). For acquire SAs,
this decrements esw->offloads.num_block_mode without a matching increment.

Return directly after installing the acquire SA offload handle, so only the
paths that successfully called mlx5_eswitch_block_mode() call the matching
unblock.

## References
- https://git.kernel.org/stable/c/abe003b33223ff33552f291644bf35d9c2f992fb
- https://git.kernel.org/stable/c/b5bd4249e430f5963d559708ee96a671716d2400
- https://git.kernel.org/stable/c/ecafd8284e527666e83261e6e57a7c7341d591cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64522
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
