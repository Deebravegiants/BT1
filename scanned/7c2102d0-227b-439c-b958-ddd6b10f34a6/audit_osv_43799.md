# [C] riscv: lib: Fix ZBB strnlen reading past count boundary

## Summary
Severity: Critical
Advisory: CVE-2026-74751
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74751
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: lib: Fix ZBB strnlen reading past count boundary

The ZBB-optimized strnlen loop loads one word ahead before checking the
aligned boundary:

    REG_L   t1, SZREG(t0)       // load next word
    addi    t0, t0, SZREG       // advance
    orc.b   t1, t1
    bgeu    t0, t4, 4f          // boundary check AFTER load

where t4 = (s + count) & -SZREG.  When s is aligned and count is a
multiple of SZREG, t4 equals s + count and the loop loads a full word
starting at exactly s + count.  If s + count falls on a page boundary
with the next page unmapped, this faults.

Fix by computing the aligned boundary from the last valid byte
(s + count - 1) instead of s + count.  This makes the loop stop at the
word containing the last valid byte rather than potentially loading the
word after it.  The count == 0 case is already handled by the beqz
early exit.

Also add a pre-loop guard (bgeu t0, t4) for the case where all valid
bytes fit within the first word.  With the adjusted boundary, t4 can
equal t0, and entering the loop with stale register state from the
first-word processing would produce incorrect results.

The final minu clamp ensures the result is still correct when the last
loaded word extends past s + count - 1 within the same aligned word.

## References
- https://git.kernel.org/stable/c/5d588c684833e678a0008eb69c33190f01a65f4b
- https://git.kernel.org/stable/c/e697e30f3dd2da3a1df7dc0980546d5b53aea4b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74751.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74751
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
