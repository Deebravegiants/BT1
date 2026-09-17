# [H] CVE-2021-47311

## Summary
Severity: High
Advisory: CVE-2021-47311
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47311
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qcom/emac: fix UAF in emac_remove

adpt is netdev private data and it cannot be
used after free_netdev() call. Using adpt after free_netdev()
can cause UAF bug. Fix it by moving free_netdev() at the end of the
function.

## References
- https://git.kernel.org/stable/c/b1e091331920f8fbfc747dcbd16263fcd71abb2d
- https://git.kernel.org/stable/c/b560521eca03d0a2db6093a5a632cbdd0a0cf833
- https://git.kernel.org/stable/c/11e9d163d631198bb3eb41a677a61b499516c0f7
- https://git.kernel.org/stable/c/2b70ca92847c619d6264c7372ef74fcbfd1e048c
- https://git.kernel.org/stable/c/4d04a42b926e682140776e54188f4a44f1f01a81
- https://git.kernel.org/stable/c/8a225a6e07a57a1538d53637cb3d82bd3e477839
- https://git.kernel.org/stable/c/ad297cd2db8953e2202970e9504cab247b6c7cb4
