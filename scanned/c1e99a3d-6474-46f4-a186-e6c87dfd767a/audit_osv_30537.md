# [H] bpf: sync_linked_regs() must preserve subreg_def

## Summary
Severity: High
Advisory: CVE-2024-53125
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53125
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.232, >=5.11.0 <5.15.175, >=5.16.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: sync_linked_regs() must preserve subreg_def

Range propagation must not affect subreg_def marks, otherwise the
following example is rewritten by verifier incorrectly when
BPF_F_TEST_RND_HI32 flag is set:

  0: call bpf_ktime_get_ns                   call bpf_ktime_get_ns
  1: r0 &= 0x7fffffff       after verifier   r0 &= 0x7fffffff
  2: w1 = w0                rewrites         w1 = w0
  3: if w0 < 10 goto +0     -------------->  r11 = 0x2f5674a6     (r)
  4: r1 >>= 32                               r11 <<= 32           (r)
  5: r0 = r1                                 r1 |= r11            (r)
  6: exit;                                   if w0 < 0xa goto pc+0
                                             r1 >>= 32
                                             r0 = r1
                                             exit

(or zero extension of w1 at (2) is missing for architectures that
 require zero extension for upper register half).

The following happens w/o this patch:
- r0 is marked as not a subreg at (0);
- w1 is marked as subreg at (2);
- w1 subreg_def is overridden at (3) by copy_register_state();
- w1 is read at (5) but mark_insn_zext() does not mark (2)
  for zero extension, because w1 subreg_def is not set;
- because of BPF_F_TEST_RND_HI32 flag verifier inserts random
  value for hi32 bits of (2) (marked (r));
- this random value is read at (5).

## References
- https://git.kernel.org/stable/c/60fd3538d2a8fd44c41d25088c0ece3e1fd30659
- https://git.kernel.org/stable/c/b57ac2d92c1f565743f6890a5b9cf317ed856b09
- https://git.kernel.org/stable/c/bfe9446ea1d95f6cb7848da19dfd58d2eec6fd84
- https://git.kernel.org/stable/c/dadf82c1b2608727bcc306843b540cd7414055a7
- https://git.kernel.org/stable/c/e2ef0f317a52e678fe8fa84b94d6a15b466d6ff0
- https://git.kernel.org/stable/c/e9bd9c498cb0f5843996dbe5cbce7a1836a83c70
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53125.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53125
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
