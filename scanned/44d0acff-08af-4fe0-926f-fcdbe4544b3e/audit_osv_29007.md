# [H] openrisc: traps: Don't send signals to kernel mode threads

## Summary
Severity: High
Advisory: CVE-2024-38614
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38614
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

openrisc: traps: Don't send signals to kernel mode threads

OpenRISC exception handling sends signals to user processes on floating
point exceptions and trap instructions (for debugging) among others.
There is a bug where the trap handling logic may send signals to kernel
threads, we should not send these signals to kernel threads, if that
happens we treat it as an error.

This patch adds conditions to die if the kernel receives these
exceptions in kernel mode code.

## References
- https://git.kernel.org/stable/c/075c0405b0d7d9fc490609e988a3af0069596538
- https://git.kernel.org/stable/c/c0ed9a711e3392d73e857faa031d8d349c0d70db
- https://git.kernel.org/stable/c/c88cfb5cea5f8f9868ef02cc9ce9183a26dcf20f
- https://git.kernel.org/stable/c/cea9d0015c140af39477dd5eeb9b20233a45daa9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38614.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38614
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
