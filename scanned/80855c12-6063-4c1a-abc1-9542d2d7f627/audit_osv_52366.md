# [M] CVE-2021-47373

## Summary
Severity: Medium
Advisory: CVE-2021-47373
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47373
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gic-v3-its: Fix potential VPE leak on error

In its_vpe_irq_domain_alloc, when its_vpe_init() returns an error,
there is an off-by-one in the number of VPEs to be freed.

Fix it by simply passing the number of VPEs allocated, which is the
index of the loop iterating over the VPEs.

[maz: fixed commit message]

## References
- https://git.kernel.org/stable/c/7d39992d45acd6f2d6b2f62389c55b61fb3d486b
- https://git.kernel.org/stable/c/e0c1c2e5da19685a20557a50f10c6aa4fa26aa84
- https://git.kernel.org/stable/c/280bef512933b2dda01d681d8cbe499b98fc5bdd
- https://git.kernel.org/stable/c/42d3711c23781045e7a5cd28536c774b9a66d20b
- https://git.kernel.org/stable/c/568662e37f927e3dc3e475f3ff7cf4ab7719c5e7
- https://git.kernel.org/stable/c/5701e8bff314c155e7afdc467b1e0389d86853d0
