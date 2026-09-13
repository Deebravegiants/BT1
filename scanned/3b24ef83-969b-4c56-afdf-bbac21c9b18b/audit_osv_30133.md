# [H] arm64: probes: Remove broken LDR (literal) uprobe support

## Summary
Severity: High
Advisory: CVE-2024-50099
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50099
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: probes: Remove broken LDR (literal) uprobe support

The simulate_ldr_literal() and simulate_ldrsw_literal() functions are
unsafe to use for uprobes. Both functions were originally written for
use with kprobes, and access memory with plain C accesses. When uprobes
was added, these were reused unmodified even though they cannot safely
access user memory.

There are three key problems:

1) The plain C accesses do not have corresponding extable entries, and
   thus if they encounter a fault the kernel will treat these as
   unintentional accesses to user memory, resulting in a BUG() which
   will kill the kernel thread, and likely lead to further issues (e.g.
   lockup or panic()).

2) The plain C accesses are subject to HW PAN and SW PAN, and so when
   either is in use, any attempt to simulate an access to user memory
   will fault. Thus neither simulate_ldr_literal() nor
   simulate_ldrsw_literal() can do anything useful when simulating a
   user instruction on any system with HW PAN or SW PAN.

3) The plain C accesses are privileged, as they run in kernel context,
   and in practice can access a small range of kernel virtual addresses.
   The instructions they simulate have a range of +/-1MiB, and since the
   simulated instructions must itself be a user instructions in the
   TTBR0 address range, these can address the final 1MiB of the TTBR1
   acddress range by wrapping downwards from an address in the first
   1MiB of the TTBR0 address range.

   In contemporary kernels the last 8MiB of TTBR1 address range is
   reserved, and accesses to this will always fault, meaning this is no
   worse than (1).

   Historically, it was theoretically possible for the linear map or
   vmemmap to spill into the final 8MiB of the TTBR1 address range, but
   in practice this is extremely unlikely to occur as this would
   require either:

   * Having enough physical memory to fill the entire linear map all the
     way to the final 1MiB of the TTBR1 address range.

   * Getting unlucky with KASLR randomization of the linear map such
     that the populated region happens to overlap with the last 1MiB of
     the TTBR address range.

   ... and in either case if we were to spill into the final page there
   would be larger problems as the final page would alias with error
   pointers.

Practically speaking, (1) and (2) are the big issues. Given there have
been no reports of problems since the broken code was introduced, it
appears that no-one is relying on probing these instructions with
uprobes.

Avoid these issues by not allowing uprobes on LDR (literal) and LDRSW
(literal), limiting the use of simulate_ldr_literal() and
simulate_ldrsw_literal() to kprobes. Attempts to place uprobes on LDR
(literal) and LDRSW (literal) will be rejected as
arm_probe_decode_insn() will return INSN_REJECTED. In future we can
consider introducing working uprobes support for these instructions, but
this will require more significant work.

## References
- https://git.kernel.org/stable/c/20cde998315a3d2df08e26079a3ea7501abce6db
- https://git.kernel.org/stable/c/3728b4eb27910ffedd173018279a970705f2e03a
- https://git.kernel.org/stable/c/9f1e7735474e7457a4d919a517900e46868ae5f6
- https://git.kernel.org/stable/c/acc450aa07099d071b18174c22a1119c57da8227
- https://git.kernel.org/stable/c/ad4bc35a6d22e9ff9b67d0d0c38bce654232f195
- https://git.kernel.org/stable/c/ae743deca78d9e4b7f4f60ad2f95e20e8ea057f9
- https://git.kernel.org/stable/c/bae792617a7e911477f67a3aff850ad4ddf51572
- https://git.kernel.org/stable/c/cc86f2e9876c8b5300238cec6bf0bd8c842078ee
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50099.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
