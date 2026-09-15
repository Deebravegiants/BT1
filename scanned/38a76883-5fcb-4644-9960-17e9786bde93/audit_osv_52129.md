# [M] CVE-2021-47105

## Summary
Severity: Medium
Advisory: CVE-2021-47105
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47105
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: xsk: return xsk buffers back to pool when cleaning the ring

Currently we only NULL the xdp_buff pointer in the internal SW ring but
we never give it back to the xsk buffer pool. This means that buffers
can be leaked out of the buff pool and never be used again.

Add missing xsk_buff_free() call to the routine that is supposed to
clean the entries that are left in the ring so that these buffers in the
umem can be used by other sockets.

Also, only go through the space that is actually left to be cleaned
instead of a whole ring.

## References
- https://git.kernel.org/stable/c/ad6d20da2cfbe14b7b1200d15f39e65988b0b9e8
- https://git.kernel.org/stable/c/afe8a3ba85ec2a6b6849367e25c06a2f8e0ddd05
