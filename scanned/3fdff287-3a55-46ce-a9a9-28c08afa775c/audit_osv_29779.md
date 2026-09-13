# [C] net/mlx5e: SHAMPO, Fix incorrect page release

## Summary
Severity: Critical
Advisory: CVE-2024-46717
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46717
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.109, >=6.2.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: SHAMPO, Fix incorrect page release

Under the following conditions:
1) No skb created yet
2) header_size == 0 (no SHAMPO header)
3) header_index + 1 % MLX5E_SHAMPO_WQ_HEADER_PER_PAGE == 0 (this is the
   last page fragment of a SHAMPO header page)

a new skb is formed with a page that is NOT a SHAMPO header page (it
is a regular data page). Further down in the same function
(mlx5e_handle_rx_cqe_mpwrq_shampo()), a SHAMPO header page from
header_index is released. This is wrong and it leads to SHAMPO header
pages being released more than once.

## References
- https://git.kernel.org/stable/c/03924d117625ecb10ee3c9b65930bcb2c37ae629
- https://git.kernel.org/stable/c/70bd03b89f20b9bbe51a7f73c4950565a17a45f7
- https://git.kernel.org/stable/c/ae9018e3f61ba5cc1f08a6e51d3c0bef0a79f3ab
- https://git.kernel.org/stable/c/c909ab41df2b09cde919801c7a7b6bb2cc37ea22
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46717.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
