# [H] bpf: Fix UAF via mismatching bpf_prog/attachment RCU flavors

## Summary
Severity: High
Advisory: CVE-2024-56675
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56675
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix UAF via mismatching bpf_prog/attachment RCU flavors

Uprobes always use bpf_prog_run_array_uprobe() under tasks-trace-RCU
protection. But it is possible to attach a non-sleepable BPF program to a
uprobe, and non-sleepable BPF programs are freed via normal RCU (see
__bpf_prog_put_noref()). This leads to UAF of the bpf_prog because a normal
RCU grace period does not imply a tasks-trace-RCU grace period.

Fix it by explicitly waiting for a tasks-trace-RCU grace period after
removing the attachment of a bpf_prog to a perf_event.

## References
- https://git.kernel.org/stable/c/9245459a992d22fe0e92e988f49db1fec82c184a
- https://git.kernel.org/stable/c/9b53d2c2a38a1effc341d99be3f99fa7ef17047d
- https://git.kernel.org/stable/c/ef1b808e3b7c98612feceedf985c2fbbeb28f956
- https://git.kernel.org/stable/c/f9f85df30118f3f4112761e6682fc60ebcce23e5
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56675.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56675
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
