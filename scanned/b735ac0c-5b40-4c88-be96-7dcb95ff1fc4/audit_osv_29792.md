# [H] bpf: Remove tst_run from lwt_seg6local_prog_ops.

## Summary
Severity: High
Advisory: CVE-2024-46754
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46754
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.269, >=5.11.0 <5.15.220, >=5.16.0 <6.1.187, >=6.2.0 <6.6.156, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Remove tst_run from lwt_seg6local_prog_ops.

The syzbot reported that the lwt_seg6 related BPF ops can be invoked
via bpf_test_run() without without entering input_action_end_bpf()
first.

Martin KaFai Lau said that self test for BPF_PROG_TYPE_LWT_SEG6LOCAL
probably didn't work since it was introduced in commit 04d4b274e2a
("ipv6: sr: Add seg6local action End.BPF"). The reason is that the
per-CPU variable seg6_bpf_srh_states::srh is never assigned in the self
test case but each BPF function expects it.

Remove test_run for BPF_PROG_TYPE_LWT_SEG6LOCAL.

## References
- https://git.kernel.org/stable/c/9cd15511de7c619bbd0f54bb3f28e6e720ded5d6
- https://git.kernel.org/stable/c/a675524cfbe88fd49c05ff8807a08646983e687c
- https://git.kernel.org/stable/c/b05c2e25a5c168dbb46b6f7fcb741fd4e4f3b54a
- https://git.kernel.org/stable/c/c13fda93aca118b8e5cd202e339046728ee7dddb
- https://git.kernel.org/stable/c/e217492f6fa2228ad703ee3006d8fc4e5969fbd4
- https://git.kernel.org/stable/c/ea3fae6984ba0f054550e4da22219489c12cd8d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46754.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46754
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
