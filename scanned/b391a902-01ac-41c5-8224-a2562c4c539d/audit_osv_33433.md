# [C] net/mlx5e: RX, Fix generating skb from non-linear xdp_buff for striding RQ

## Summary
Severity: Critical
Advisory: CVE-2025-40350
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-40350
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.115, >=6.7.0 <6.12.56, >=6.13.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: RX, Fix generating skb from non-linear xdp_buff for striding RQ

XDP programs can change the layout of an xdp_buff through
bpf_xdp_adjust_tail() and bpf_xdp_adjust_head(). Therefore, the driver
cannot assume the size of the linear data area nor fragments. Fix the
bug in mlx5 by generating skb according to xdp_buff after XDP programs
run.

Currently, when handling multi-buf XDP, the mlx5 driver assumes the
layout of an xdp_buff to be unchanged. That is, the linear data area
continues to be empty and fragments remain the same. This may cause
the driver to generate erroneous skb or triggering a kernel
warning. When an XDP program added linear data through
bpf_xdp_adjust_head(), the linear data will be ignored as
mlx5e_build_linear_skb() builds an skb without linear data and then
pull data from fragments to fill the linear data area. When an XDP
program has shrunk the non-linear data through bpf_xdp_adjust_tail(),
the delta passed to __pskb_pull_tail() may exceed the actual nonlinear
data size and trigger the BUG_ON in it.

To fix the issue, first record the original number of fragments. If the
number of fragments changes after the XDP program runs, rewind the end
fragment pointer by the difference and recalculate the truesize. Then,
build the skb with the linear data area matching the xdp_buff. Finally,
only pull data in if there is non-linear data and fill the linear part
up to 256 bytes.

## References
- https://git.kernel.org/stable/c/87bcef158ac1faca1bd7e0104588e8e2956d10be
- https://git.kernel.org/stable/c/8b051d7f530e8a5237da242fbeafef02fec6b813
- https://git.kernel.org/stable/c/cb9edd583e23979ee546981be963ad5f217e8b18
- https://git.kernel.org/stable/c/f2557d7fa38e9475b38588f5c124476091480f53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40350.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40350
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
