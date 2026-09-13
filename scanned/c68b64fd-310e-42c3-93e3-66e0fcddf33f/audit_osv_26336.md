# [H] x86/tdx: Zero out the missing RSI in TDX_HYPERCALL macro

## Summary
Severity: High
Advisory: CVE-2023-52874
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52874
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/tdx: Zero out the missing RSI in TDX_HYPERCALL macro

In the TDX_HYPERCALL asm, after the TDCALL instruction returns from the
untrusted VMM, the registers that the TDX guest shares to the VMM need
to be cleared to avoid speculative execution of VMM-provided values.

RSI is specified in the bitmap of those registers, but it is missing
when zeroing out those registers in the current TDX_HYPERCALL.

It was there when it was originally added in commit 752d13305c78
("x86/tdx: Expand __tdx_hypercall() to handle more arguments"), but was
later removed in commit 1e70c680375a ("x86/tdx: Do not corrupt
frame-pointer in __tdx_hypercall()"), which was correct because %rsi is
later restored in the "pop %rsi".  However a later commit 7a3a401874be
("x86/tdx: Drop flags from __tdx_hypercall()") removed that "pop %rsi"
but forgot to add the "xor %rsi, %rsi" back.

Fix by adding it back.

## References
- https://git.kernel.org/stable/c/2191950d35d8f81620ea8d4e04d983f664fe3a8a
- https://git.kernel.org/stable/c/5d092b66119d774853cc9308522620299048a662
- https://git.kernel.org/stable/c/de4c5bacca4f50233f1f791bec9eeb4dee1b14cd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52874.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52874
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
