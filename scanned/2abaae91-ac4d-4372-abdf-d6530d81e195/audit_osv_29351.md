# [H] bpf: Fix may_goto with negative offset.

## Summary
Severity: High
Advisory: CVE-2024-42072
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42072
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix may_goto with negative offset.

Zac's syzbot crafted a bpf prog that exposed two bugs in may_goto.
The 1st bug is the way may_goto is patched. When offset is negative
it should be patched differently.
The 2nd bug is in the verifier:
when current state may_goto_depth is equal to visited state may_goto_depth
it means there is an actual infinite loop. It's not correct to prune
exploration of the program at this point.
Note, that this check doesn't limit the program to only one may_goto insn,
since 2nd and any further may_goto will increment may_goto_depth only
in the queued state pushed for future exploration. The current state
will have may_goto_depth == 0 regardless of number of may_goto insns
and the verifier has to explore the program until bpf_exit.

## References
- https://git.kernel.org/stable/c/175827e04f4be53f3dfb57edf12d0d49b18fd939
- https://git.kernel.org/stable/c/2b2efe1937ca9f8815884bd4dcd5b32733025103
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42072.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
