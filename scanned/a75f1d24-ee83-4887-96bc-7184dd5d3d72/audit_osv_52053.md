# [H] CVE-2021-47012

## Summary
Severity: High
Advisory: CVE-2021-47012
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47012
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Fix a use after free in siw_alloc_mr

Our code analyzer reported a UAF.

In siw_alloc_mr(), it calls siw_mr_add_mem(mr,..). In the implementation of
siw_mr_add_mem(), mem is assigned to mr->mem and then mem is freed via
kfree(mem) if xa_alloc_cyclic() failed. Here, mr->mem still point to a
freed object. After, the execution continue up to the err_out branch of
siw_alloc_mr, and the freed mr->mem is used in siw_mr_drop_mem(mr).

My patch moves "mr->mem = mem" behind the if (xa_alloc_cyclic(..)<0) {}
section, to avoid the uaf.

## References
- https://git.kernel.org/stable/c/3093ee182f01689b89e9f8797b321603e5de4f63
- https://git.kernel.org/stable/c/30b9e92d0b5e5d5dc1101ab856c17009537cbca4
- https://git.kernel.org/stable/c/3e22b88e02c194f6c80867abfef5cc09383461f4
- https://git.kernel.org/stable/c/608a4b90ece039940e9425ee2b39c8beff27e00c
- https://git.kernel.org/stable/c/ad9ce7188432650469a6c7625bf479f5ed0b6155
