# [H] nvme-fc: use lock accessing port_state and rport state

## Summary
Severity: High
Advisory: CVE-2025-40342
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-40342
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-fc: use lock accessing port_state and rport state

nvme_fc_unregister_remote removes the remote port on a lport object at
any point in time when there is no active association. This races with
with the reconnect logic, because nvme_fc_create_association is not
taking a lock to check the port_state and atomically increase the
active count on the rport.

## References
- https://git.kernel.org/stable/c/25f4bf1f7979a7871974fd36c79d69ff1cf4b446
- https://git.kernel.org/stable/c/4253e0a4546138a2bf9cb6acf66b32fee677fc7c
- https://git.kernel.org/stable/c/891cdbb162ccdb079cd5228ae43bdeebce8597ad
- https://git.kernel.org/stable/c/9950af4303942081dc8c7a5fdc3688c17c7eb6c0
- https://git.kernel.org/stable/c/a2f7fa75c4a2a07328fa22ccbef461db76790b55
- https://git.kernel.org/stable/c/de3d91af47bc015031e7721b100a29989f6498a5
- https://git.kernel.org/stable/c/e8cde03de8674b05f2c5e0870729049eba517800
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40342.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40342
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
