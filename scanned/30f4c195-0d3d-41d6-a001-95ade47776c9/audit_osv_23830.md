# [H] bpf: Fix potential array overflow in bpf_trampoline_get_progs()

## Summary
Severity: High
Advisory: CVE-2022-49548
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49548
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.120, >=5.11.0 <5.15.45, >=5.16.0 <5.17.13, >=5.18.0 <5.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix potential array overflow in bpf_trampoline_get_progs()

The cnt value in the 'cnt >= BPF_MAX_TRAMP_PROGS' check does not
include BPF_TRAMP_MODIFY_RETURN bpf programs, so the number of
the attached BPF_TRAMP_MODIFY_RETURN bpf programs in a trampoline
can exceed BPF_MAX_TRAMP_PROGS.

When this happens, the assignment '*progs++ = aux->prog' in
bpf_trampoline_get_progs() will cause progs array overflow as the
progs field in the bpf_tramp_progs struct can only hold at most
BPF_MAX_TRAMP_PROGS bpf programs.

## References
- https://git.kernel.org/stable/c/32c4559c61652f24c9fdd5440342196fe37453bc
- https://git.kernel.org/stable/c/4f8897bcc20b9ae44758e0572538d741ab66f0dc
- https://git.kernel.org/stable/c/7f845de2863334bed4f362e95853f5e7bc323737
- https://git.kernel.org/stable/c/a2aa95b71c9bbec793b5c5fa50f0a80d882b3e8d
- https://git.kernel.org/stable/c/e36452d5da6325df7c10cffc60a9e68d21e2606d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49548.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49548
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
