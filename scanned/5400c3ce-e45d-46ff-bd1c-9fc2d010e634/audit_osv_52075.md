# [M] CVE-2021-47043

## Summary
Severity: Medium
Advisory: CVE-2021-47043
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47043
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: core: Fix some resource leaks in the error path of 'venus_probe()'

If an error occurs after a successful 'of_icc_get()' call, it must be
undone.

Use 'devm_of_icc_get()' instead of 'of_icc_get()' to avoid the leak.
Update the remove function accordingly and axe the now unneeded
'icc_put()' calls.

## References
- https://git.kernel.org/stable/c/940d01eceb3a7866fbfca136a55a5625fc75a565
- https://git.kernel.org/stable/c/00b68a7478343afdf83f30c43e64db5296057030
- https://git.kernel.org/stable/c/5a465c5391a856a0c1e9554964d660676c35d1b2
- https://git.kernel.org/stable/c/711acdf0228dc71601247f28b56f13e850e395c8
