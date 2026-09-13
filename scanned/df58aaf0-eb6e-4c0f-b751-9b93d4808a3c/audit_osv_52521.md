# [M] CVE-2021-47537

## Summary
Severity: Medium
Advisory: CVE-2021-47537
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47537
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: Fix a memleak bug in rvu_mbox_init()

In rvu_mbox_init(), mbox_regions is not freed or passed out
under the switch-default region, which could lead to a memory leak.

Fix this bug by changing 'return err' to 'goto free_regions'.

This bug was found by a static analyzer. The analysis employs
differential checking to identify inconsistent security operations
(e.g., checks or kfrees) between two code paths and confirms that the
inconsistent operations are not recovered in the current function or
the callers, so they constitute bugs.

Note that, as a bug found by static analysis, it can be a false
positive or hard to trigger. Multiple researchers have cross-reviewed
the bug.

Builds with CONFIG_OCTEONTX2_AF=y show no new warnings,
and our static analyzer no longer warns about this code.

## References
- https://git.kernel.org/stable/c/1c0ddef45b7e3dbe3ed073695d20faa572b7056a
- https://git.kernel.org/stable/c/e07a097b4986afb8f925d0bb32612e1d3e88ce15
