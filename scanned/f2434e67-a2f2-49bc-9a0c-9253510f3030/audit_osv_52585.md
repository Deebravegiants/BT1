# [M] CVE-2021-47607

## Summary
Severity: Medium
Advisory: CVE-2021-47607
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47607
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix kernel address leakage in atomic cmpxchg's r0 aux reg

The implementation of BPF_CMPXCHG on a high level has the following parameters:

  .-[old-val]                                          .-[new-val]
  BPF_R0 = cmpxchg{32,64}(DST_REG + insn->off, BPF_R0, SRC_REG)
                          `-[mem-loc]          `-[old-val]

Given a BPF insn can only have two registers (dst, src), the R0 is fixed and
used as an auxilliary register for input (old value) as well as output (returning
old value from memory location). While the verifier performs a number of safety
checks, it misses to reject unprivileged programs where R0 contains a pointer as
old value.

Through brute-forcing it takes about ~16sec on my machine to leak a kernel pointer
with BPF_CMPXCHG. The PoC is basically probing for kernel addresses by storing the
guessed address into the map slot as a scalar, and using the map value pointer as
R0 while SRC_REG has a canary value to detect a matching address.

Fix it by checking R0 for pointers, and reject if that's the case for unprivileged
programs.

## References
- https://git.kernel.org/stable/c/a82fe085f344ef20b452cd5f481010ff96b5c4cd
- https://git.kernel.org/stable/c/f87a6c160ecc8c7b417d25f508d3f076fe346136
