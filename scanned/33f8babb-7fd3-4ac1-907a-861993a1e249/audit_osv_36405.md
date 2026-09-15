# [H] clsact: Fix use-after-free in init/destroy rollback asymmetry

## Summary
Severity: High
Advisory: CVE-2026-23413
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-23413
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.130, >=6.7.0 <6.12.78, >=6.10.0 <6.18.20, >=6.13.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

clsact: Fix use-after-free in init/destroy rollback asymmetry

Fix a use-after-free in the clsact qdisc upon init/destroy rollback asymmetry.
The latter is achieved by first fully initializing a clsact instance, and
then in a second step having a replacement failure for the new clsact qdisc
instance. clsact_init() initializes ingress first and then takes care of the
egress part. This can fail midway, for example, via tcf_block_get_ext(). Upon
failure, the kernel will trigger the clsact_destroy() callback.

Commit 1cb6f0bae504 ("bpf: Fix too early release of tcx_entry") details the
way how the transition is happening. If tcf_block_get_ext on the q->ingress_block
ends up failing, we took the tcx_miniq_inc reference count on the ingress
side, but not yet on the egress side. clsact_destroy() tests whether the
{ingress,egress}_entry was non-NULL. However, even in midway failure on the
replacement, both are in fact non-NULL with a valid egress_entry from the
previous clsact instance.

What we really need to test for is whether the qdisc instance-specific ingress
or egress side previously got initialized. This adds a small helper for checking
the miniq initialization called mini_qdisc_pair_inited, and utilizes that upon
clsact_destroy() in order to fix the use-after-free scenario. Convert the
ingress_destroy() side as well so both are consistent to each other.

## References
- https://git.kernel.org/stable/c/0509b762bc5e8ea7b8391130730c6d8502fc6e69
- https://git.kernel.org/stable/c/37bef86e5428d59f70a4da82b80f9a8f252fecbe
- https://git.kernel.org/stable/c/4c9af67f99aa3e51b522c54968ab3ac8272be41c
- https://git.kernel.org/stable/c/a0671125d4f55e1e98d9bde8a0b671941987e208
- https://git.kernel.org/stable/c/a73d95b57bf9faebdfed591bcb7ed9292062a84c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23413.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23413
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
