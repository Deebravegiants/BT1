# [H] bpf: support deferring bpf_link dealloc to after RCU grace period

## Summary
Severity: High
Advisory: CVE-2024-35860
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35860
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: support deferring bpf_link dealloc to after RCU grace period

BPF link for some program types is passed as a "context" which can be
used by those BPF programs to look up additional information. E.g., for
multi-kprobes and multi-uprobes, link is used to fetch BPF cookie values.

Because of this runtime dependency, when bpf_link refcnt drops to zero
there could still be active BPF programs running accessing link data.

This patch adds generic support to defer bpf_link dealloc callback to
after RCU GP, if requested. This is done by exposing two different
deallocation callbacks, one synchronous and one deferred. If deferred
one is provided, bpf_link_free() will schedule dealloc_deferred()
callback to happen after RCU GP.

BPF is using two flavors of RCU: "classic" non-sleepable one and RCU
tasks trace one. The latter is used when sleepable BPF programs are
used. bpf_link_free() accommodates that by checking underlying BPF
program's sleepable flag, and goes either through normal RCU GP only for
non-sleepable, or through RCU tasks trace GP *and* then normal RCU GP
(taking into account rcu_trace_implies_rcu_gp() optimization), if BPF
program is sleepable.

We use this for multi-kprobe and multi-uprobe links, which dereference
link during program run. We also preventively switch raw_tp link to use
deferred dealloc callback, as upcoming changes in bpf-next tree expose
raw_tp link data (specifically, cookie value) to BPF program at runtime
as well.

## References
- https://git.kernel.org/stable/c/1a80dbcb2dbaf6e4c216e62e30fa7d3daa8001ce
- https://git.kernel.org/stable/c/5d8d447777564b35f67000e7838e7ccb64d525c8
- https://git.kernel.org/stable/c/876941f533e7b47fc69977fc4551c02f2d18af97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35860.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35860
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
