# [M] CVE-2021-47542

## Summary
Severity: Medium
Advisory: CVE-2021-47542
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47542
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qlogic: qlcnic: Fix a NULL pointer dereference in qlcnic_83xx_add_rings()

In qlcnic_83xx_add_rings(), the indirect function of
ahw->hw_ops->alloc_mbx_args will be called to allocate memory for
cmd.req.arg, and there is a dereference of it in qlcnic_83xx_add_rings(),
which could lead to a NULL pointer dereference on failure of the
indirect function like qlcnic_83xx_alloc_mbx_args().

Fix this bug by adding a check of alloc_mbx_args(), this patch
imitates the logic of mbx_cmd()'s failure handling.

This bug was found by a static analyzer. The analysis employs
differential checking to identify inconsistent security operations
(e.g., checks or kfrees) between two code paths and confirms that the
inconsistent operations are not recovered in the current function or
the callers, so they constitute bugs.

Note that, as a bug found by static analysis, it can be a false
positive or hard to trigger. Multiple researchers have cross-reviewed
the bug.

Builds with CONFIG_QLCNIC=m show no new warnings, and our
static analyzer no longer warns about this code.

## References
- https://git.kernel.org/stable/c/57af54a56024435d83e44c78449513b414eb6edf
- https://git.kernel.org/stable/c/b4f217d6fcc00c3fdc0921a7691f30be7490b073
- https://git.kernel.org/stable/c/bbeb0325a7460ebf1e03f5e0bfc5c652fba9519f
- https://git.kernel.org/stable/c/c5ef33c1489b2cd74368057fa00b5d2183bb5853
- https://git.kernel.org/stable/c/e2dabc4f7e7b60299c20a36d6a7b24ed9bf8e572
- https://git.kernel.org/stable/c/15fa12c119f869173f9b710cbe6a4a14071d2105
- https://git.kernel.org/stable/c/3a061d54e260b701b538873b43e399d9b8b83e03
- https://git.kernel.org/stable/c/550658a2d61e4eaf522c8ebc7fad76dc376bfb45
