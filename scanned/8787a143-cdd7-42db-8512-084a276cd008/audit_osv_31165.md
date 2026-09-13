# [H] bpf: check changes_pkt_data property for extension programs

## Summary
Severity: High
Advisory: CVE-2024-58100
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-05
Source: https://osv.dev/vulnerability/CVE-2024-58100
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.6.90, >=6.7.0 <6.12.25

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: check changes_pkt_data property for extension programs

When processing calls to global sub-programs, verifier decides whether
to invalidate all packet pointers in current state depending on the
changes_pkt_data property of the global sub-program.

Because of this, an extension program replacing a global sub-program
must be compatible with changes_pkt_data property of the sub-program
being replaced.

This commit:
- adds changes_pkt_data flag to struct bpf_prog_aux:
  - this flag is set in check_cfg() for main sub-program;
  - in jit_subprogs() for other sub-programs;
- modifies bpf_check_attach_btf_id() to check changes_pkt_data flag;
- moves call to check_attach_btf_id() after the call to check_cfg(),
  because it needs changes_pkt_data flag to be set:

    bpf_check:
      ...                             ...
    - check_attach_btf_id             resolve_pseudo_ldimm64
      resolve_pseudo_ldimm64   -->    bpf_prog_is_offloaded
      bpf_prog_is_offloaded           check_cfg
      check_cfg                     + check_attach_btf_id
      ...                             ...

The following fields are set by check_attach_btf_id():
- env->ops
- prog->aux->attach_btf_trace
- prog->aux->attach_func_name
- prog->aux->attach_func_proto
- prog->aux->dst_trampoline
- prog->aux->mod
- prog->aux->saved_dst_attach_type
- prog->aux->saved_dst_prog_type
- prog->expected_attach_type

Neither of these fields are used by resolve_pseudo_ldimm64() or
bpf_prog_offload_verifier_prep() (for netronome and netdevsim
drivers), so the reordering is safe.

## References
- https://git.kernel.org/stable/c/3846e2bea565ee1c5195dcc625fda9868fb0e3b3
- https://git.kernel.org/stable/c/7197fc4acdf238ec8ad06de5a8235df0c1f9c7d7
- https://git.kernel.org/stable/c/81f6d0530ba031b5f038a091619bf2ff29568852
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58100.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
