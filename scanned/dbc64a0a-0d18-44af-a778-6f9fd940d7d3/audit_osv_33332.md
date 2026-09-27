# [H] bpf: Enforce expected_attach_type for tailcall compatibility

## Summary
Severity: High
Advisory: CVE-2025-40123
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40123
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Enforce expected_attach_type for tailcall compatibility

Yinhao et al. recently reported:

  Our fuzzer tool discovered an uninitialized pointer issue in the
  bpf_prog_test_run_xdp() function within the Linux kernel's BPF subsystem.
  This leads to a NULL pointer dereference when a BPF program attempts to
  deference the txq member of struct xdp_buff object.

The test initializes two programs of BPF_PROG_TYPE_XDP: progA acts as the
entry point for bpf_prog_test_run_xdp() and its expected_attach_type can
neither be of be BPF_XDP_DEVMAP nor BPF_XDP_CPUMAP. progA calls into a slot
of a tailcall map it owns. progB's expected_attach_type must be BPF_XDP_DEVMAP
to pass xdp_is_valid_access() validation. The program returns struct xdp_md's
egress_ifindex, and the latter is only allowed to be accessed under mentioned
expected_attach_type. progB is then inserted into the tailcall which progA
calls.

The underlying issue goes beyond XDP though. Another example are programs
of type BPF_PROG_TYPE_CGROUP_SOCK_ADDR. sock_addr_is_valid_access() as well
as sock_addr_func_proto() have different logic depending on the programs'
expected_attach_type. Similarly, a program attached to BPF_CGROUP_INET4_GETPEERNAME
should not be allowed doing a tailcall into a program which calls bpf_bind()
out of BPF which is only enabled for BPF_CGROUP_INET4_CONNECT.

In short, specifying expected_attach_type allows to open up additional
functionality or restrictions beyond what the basic bpf_prog_type enables.
The use of tailcalls must not violate these constraints. Fix it by enforcing
expected_attach_type in __bpf_prog_map_compatible().

Note that we only enforce this for tailcall maps, but not for BPF devmaps or
cpumaps: There, the programs are invoked through dev_map_bpf_prog_run*() and
cpu_map_bpf_prog_run*() which set up a new environment / context and therefore
these situations are not prone to this issue.

## References
- https://git.kernel.org/stable/c/08cb3dc9d2b44f153d0bcf2cb966e4a94b5d0f32
- https://git.kernel.org/stable/c/4540aed51b12bc13364149bf95f6ecef013197c0
- https://git.kernel.org/stable/c/a99de19128aec0913f3d529f529fbbff5edfaff8
- https://git.kernel.org/stable/c/c1ad19b5d8e23123503dcaf2d4342e1b90b923ad
- https://git.kernel.org/stable/c/f856c598080ba7ce1252867b8ecd6ad5bdaf9a6a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40123.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
