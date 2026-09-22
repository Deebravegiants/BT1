# [H] riscv: stacktrace: Disable KASAN checks for non-current tasks

## Summary
Severity: High
Advisory: CVE-2025-40358
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-40358
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.167, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: stacktrace: Disable KASAN checks for non-current tasks

Unwinding the stack of a task other than current, KASAN would report
"BUG: KASAN: out-of-bounds in walk_stackframe+0x41c/0x460"

There is a same issue on x86 and has been resolved by the commit
84936118bdf3 ("x86/unwind: Disable KASAN checks for non-current tasks")
The solution could be applied to RISC-V too.

This patch also can solve the issue:
https://seclists.org/oss-sec/2025/q4/23

[pjw@kernel.org: clean up checkpatch issues]

## References
- https://git.kernel.org/stable/c/060ea84a484e852b52b938f234bf9b5503a6c910
- https://git.kernel.org/stable/c/27379fcc15a10d3e3780fe79ba3fc7ed1ccd78e2
- https://git.kernel.org/stable/c/2c8d2b53866fb229b438296526ef0fa5a990e5e5
- https://git.kernel.org/stable/c/ef4d626ac59a56f8ec5cc09c1fef26f2923eec6f
- https://git.kernel.org/stable/c/f34ba22989da61186f30a40b6a82e0b3337b96fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40358.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40358
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
