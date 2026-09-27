# [H] uprobes/x86: Use proper mm_struct in __in_uprobe_trampoline

## Summary
Severity: High
Advisory: CVE-2026-72357
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72357
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

uprobes/x86: Use proper mm_struct in __in_uprobe_trampoline

In the unregister path we use __in_uprobe_trampoline check with
current->mm for the VMA lookup, which is wrong, because we are
in the tracer context, not the traced process.

Add mm_struct pointer argument to __in_uprobe_trampoline and
changing related callers to pass proper mm_struct pointer.

## References
- https://git.kernel.org/stable/c/169328645663bae30e9abad4012d52441e085a71
- https://git.kernel.org/stable/c/1acddd3e22dd6912dd5d54f80462405a1f1e6bae
- https://git.kernel.org/stable/c/c9170c83b0e0fc2065a4c2bca5bf1f90c5880156
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72357.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72357
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
