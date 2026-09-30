# [M] x86/bpf: Fix IP after emitting call depth accounting

## Summary
Severity: Medium
Advisory: CVE-2024-35903
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35903
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/bpf: Fix IP after emitting call depth accounting

Adjust the IP passed to `emit_patch` so it calculates the correct offset
for the CALL instruction if `x86_call_depth_emit_accounting` emits code.
Otherwise we will skip some instructions and most likely crash.

## References
- https://git.kernel.org/stable/c/3f9d57c771656bfd651e22edcfdb5f60e62542d4
- https://git.kernel.org/stable/c/81166178cf0a0062a22b1b3b5368183d39577028
- https://git.kernel.org/stable/c/9d98aa088386aee3db1b7b60b800c0fde0654a4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35903.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35903
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
