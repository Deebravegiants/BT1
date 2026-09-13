# [H] bpf: Fix oob access in cgroup local storage

## Summary
Severity: High
Advisory: CVE-2025-38502
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38502
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.192, >=5.16.0 <6.1.151, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix oob access in cgroup local storage

Lonial reported that an out-of-bounds access in cgroup local storage
can be crafted via tail calls. Given two programs each utilizing a
cgroup local storage with a different value size, and one program
doing a tail call into the other. The verifier will validate each of
the indivial programs just fine. However, in the runtime context
the bpf_cg_run_ctx holds an bpf_prog_array_item which contains the
BPF program as well as any cgroup local storage flavor the program
uses. Helpers such as bpf_get_local_storage() pick this up from the
runtime context:

  ctx = container_of(current->bpf_ctx, struct bpf_cg_run_ctx, run_ctx);
  storage = ctx->prog_item->cgroup_storage[stype];

  if (stype == BPF_CGROUP_STORAGE_SHARED)
    ptr = &READ_ONCE(storage->buf)->data[0];
  else
    ptr = this_cpu_ptr(storage->percpu_buf);

For the second program which was called from the originally attached
one, this means bpf_get_local_storage() will pick up the former
program's map, not its own. With mismatching sizes, this can result
in an unintended out-of-bounds access.

To fix this issue, we need to extend bpf_map_owner with an array of
storage_cookie[] to match on i) the exact maps from the original
program if the second program was using bpf_get_local_storage(), or
ii) allow the tail call combination if the second program was not
using any of the cgroup local storage maps.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/19341d5c59e8c7e8528e40f8663e99d67810473c
- https://git.kernel.org/stable/c/41688d1fc5d163a6c2c0e95c0419e2cb31a44648
- https://git.kernel.org/stable/c/66da7cee78590259b400e51a70622ccd41da7bb2
- https://git.kernel.org/stable/c/7acfa07c585e3d7a64654d38f0a5c762877d0b9b
- https://git.kernel.org/stable/c/abad3d0bad72a52137e0c350c59542d75ae4f513
- https://git.kernel.org/stable/c/c1c74584b9b4043c52e41fec415226e582d266a3
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38502.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38502
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
