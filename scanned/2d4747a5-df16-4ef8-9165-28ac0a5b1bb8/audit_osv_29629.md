# [H] bpf: Fix a kernel verifier crash in stacksafe()

## Summary
Severity: High
Advisory: CVE-2024-45020
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45020
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix a kernel verifier crash in stacksafe()

Daniel Hodges reported a kernel verifier crash when playing with sched-ext.
Further investigation shows that the crash is due to invalid memory access
in stacksafe(). More specifically, it is the following code:

    if (exact != NOT_EXACT &&
        old->stack[spi].slot_type[i % BPF_REG_SIZE] !=
        cur->stack[spi].slot_type[i % BPF_REG_SIZE])
            return false;

The 'i' iterates old->allocated_stack.
If cur->allocated_stack < old->allocated_stack the out-of-bound
access will happen.

To fix the issue add 'i >= cur->allocated_stack' check such that if
the condition is true, stacksafe() should fail. Otherwise,
cur->stack[spi].slot_type[i % BPF_REG_SIZE] memory access is legal.

## References
- https://git.kernel.org/stable/c/6e3987ac310c74bb4dd6a2fa8e46702fe505fb2b
- https://git.kernel.org/stable/c/7cad3174cc79519bf5f6c4441780264416822c08
- https://git.kernel.org/stable/c/bed2eb964c70b780fb55925892a74f26cb590b25
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45020.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45020
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
