# [C] idpf: bound interrupt-vector register fill to the allocated array

## Summary
Severity: Critical
Advisory: CVE-2026-80693
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80693
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

idpf: bound interrupt-vector register fill to the allocated array

idpf_get_reg_intr_vecs() fills the caller-allocated reg_vals[] array from
the VIRTCHNL2_OP_ALLOC_VECTORS reply in adapter->req_vec_chunks, bounding
its inner loop only by the per-chunk num_vectors. The array is sized
separately: idpf_intr_reg_init() allocates
kzalloc_objs(struct idpf_vec_regs, total_vecs) from
caps.num_allocated_vectors and only checks the returned count after the
fill. The sum of per-chunk num_vectors is never reconciled against
total_vecs, so a reply with a small num_allocated_vectors but chunks
summing higher writes past the end of reg_vals[].

Impact: a control plane (a PF or hypervisor device model) that returns a
VIRTCHNL2_OP_ALLOC_VECTORS reply whose per-chunk num_vectors sum exceeds
num_allocated_vectors writes struct idpf_vec_regs entries past the end of
the reg_vals kmalloc allocation (KASAN slab-out-of-bounds write).

Bound the fill loop to the array capacity passed in by the callers,
mirroring the sibling idpf_vport_get_q_reg(). The existing
num_regs < num_vecs check then rejects an undersized reply without the
out-of-bounds write happening first.

## References
- https://git.kernel.org/stable/c/41bb8748124d0d8ee5d8e1eace9dfbc874bc9564
- https://git.kernel.org/stable/c/9f7007ee9858c99aa43101bc8352c672fee85644
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80693.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80693
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
