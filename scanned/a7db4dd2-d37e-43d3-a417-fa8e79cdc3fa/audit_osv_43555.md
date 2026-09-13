# [H] bpf: fix BPF_PROG_QUERY OOB write and cgroup backward compat

## Summary
Severity: High
Advisory: CVE-2026-74371
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74371
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: fix BPF_PROG_QUERY OOB write and cgroup backward compat

BPF_PROG_QUERY writes back the 'query.revision' field unconditionally to
userspace. If userspace passes a smaller 'bpf_attr' structure (e.g. 40
bytes, which was the layout before the addition of 'query.revision'),
the kernel performs an out-of-bounds write.

Fix this by propagating the user-provided attribute size 'uattr_size'
down to the cgroup query handlers, and conditionally skipping writing
the revision field to userspace when the provided buffer size is
insufficient.

query.revision in bpf_mprog_query is structurally identical to the
cgroup case: a late tail field, written unconditionally.

But the backward-compat hazard is not the same.

The min-historical-size test is per command, and bpf_mprog_query only
serves attach types that were born with revision in the struct:

- tcx_prog_query -> BPF_TCX_INGRESS/EGRESS
- netkit_prog_query -> BPF_NETKIT_PRIMARY/PEER

tcx, netkit, the revision field, and bpf_mprog_query itself all landed in
the same v6.6 merge window (053c8e1f235d added the mprog query API +
revision; tcx in e420bed02507, netkit in 35dfaad7188c). There has never
been a tcx/netkit BPF_PROG_QUERY userspace that doesn't know about
revision. So for these commands the minimum legitimate struct already
covers offset 56-64 — no old binary can be broken here.

Contrast with cgroup: BPF_PROG_QUERY on cgroup attach types shipped in
2017; revision write-back was bolted on years later (120933984460). That
path has a real population of pre-revision callers.

## References
- https://git.kernel.org/stable/c/21c4b99b27f3f85b89256e81b3e997dec0a460d0
- https://git.kernel.org/stable/c/a7131340d0f95df9a541257dccab5d85e6bcdd2b
- https://git.kernel.org/stable/c/d3d630e8a7f3421bc2d204b87bdff35b4432a8e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74371.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74371
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
