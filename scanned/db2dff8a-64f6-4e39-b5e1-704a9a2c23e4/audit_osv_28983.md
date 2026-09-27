# [H] bpf: Add BPF_PROG_TYPE_CGROUP_SKB attach type enforcement in BPF_LINK_CREATE

## Summary
Severity: High
Advisory: CVE-2024-38564
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38564
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Add BPF_PROG_TYPE_CGROUP_SKB attach type enforcement in BPF_LINK_CREATE

bpf_prog_attach uses attach_type_to_prog_type to enforce proper
attach type for BPF_PROG_TYPE_CGROUP_SKB. link_create uses
bpf_prog_get and relies on bpf_prog_attach_check_attach_type
to properly verify prog_type <> attach_type association.

Add missing attach_type enforcement for the link_create case.
Otherwise, it's currently possible to attach cgroup_skb prog
types to other cgroup hooks.

## References
- https://git.kernel.org/stable/c/543576ec15b17c0c93301ac8297333c7b6e84ac7
- https://git.kernel.org/stable/c/6675c541f540a29487a802d3135280b69b9f568d
- https://git.kernel.org/stable/c/67929e973f5a347f05fef064fea4ae79e7cdb5fd
- https://git.kernel.org/stable/c/b34bbc76651065a5eafad8ddff1eb8d1f8473172
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38564.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38564
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
