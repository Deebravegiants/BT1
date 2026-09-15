# [M] ice: fix memleak in ice_init_tx_topology()

## Summary
Severity: Medium
Advisory: CVE-2024-50190
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50190
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix memleak in ice_init_tx_topology()

Fix leak of the FW blob (DDP pkg).

Make ice_cfg_tx_topo() const-correct, so ice_init_tx_topology() can avoid
copying whole FW blob. Copy just the topology section, and only when
needed. Reuse the buffer allocated for the read of the current topology.

This was found by kmemleak, with the following trace for each PF:
    [<ffffffff8761044d>] kmemdup_noprof+0x1d/0x50
    [<ffffffffc0a0a480>] ice_init_ddp_config+0x100/0x220 [ice]
    [<ffffffffc0a0da7f>] ice_init_dev+0x6f/0x200 [ice]
    [<ffffffffc0a0dc49>] ice_init+0x29/0x560 [ice]
    [<ffffffffc0a10c1d>] ice_probe+0x21d/0x310 [ice]

Constify ice_cfg_tx_topo() @buf parameter.
This cascades further down to few more functions.

## References
- https://git.kernel.org/stable/c/43544b4e30732c3d88f423252281915d5bc739b6
- https://git.kernel.org/stable/c/c188afdc36113760873ec78cbc036f6b05f77621
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50190.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50190
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
