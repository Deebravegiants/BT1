# [M] CVE-2021-47074

## Summary
Severity: Medium
Advisory: CVE-2021-47074
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-01
Source: https://osv.dev/vulnerability/CVE-2021-47074
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-loop: fix memory leak in nvme_loop_create_ctrl()

When creating loop ctrl in nvme_loop_create_ctrl(), if nvme_init_ctrl()
fails, the loop ctrl should be freed before jumping to the "out" label.

## References
- https://git.kernel.org/stable/c/03504e3b54cc8118cc26c064e60a0b00c2308708
- https://git.kernel.org/stable/c/551ba08d4b7eb26f75758cdb9f15105b276517ad
- https://git.kernel.org/stable/c/9c980795ccd77e8abec33dd6fe28dfe1c4083e65
