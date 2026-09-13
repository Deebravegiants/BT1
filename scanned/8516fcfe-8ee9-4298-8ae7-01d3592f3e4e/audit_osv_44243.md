# [H] tools/power/x86/intel-speed-select: Harden daemon pidfile open

## Summary
Severity: High
Advisory: CVE-2026-80663
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80663
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tools/power/x86/intel-speed-select: Harden daemon pidfile open

Avoid symlink-based pidfile clobbering by opening the pidfile with
O_NOFOLLOW and validating it with fstat() before locking/writing.

The daemon currently uses a fixed pidfile path under /tmp. A local
unprivileged user can pre-create a symlink at that path and cause a
root-run daemon instance to write into an attacker-chosen file.

## References
- https://git.kernel.org/stable/c/19ffeb30fdfce63f8d6aca71bcdddb3f69d46278
- https://git.kernel.org/stable/c/607af438e6430893a822964c841a1994b33acccc
- https://git.kernel.org/stable/c/72a07abc6b9046f07a08bba353cad7667bcc9dce
- https://git.kernel.org/stable/c/905493a6338c82a70da16f86e0a6215db5a3d73d
- https://git.kernel.org/stable/c/db938eb9a3c1317596c28e94413b33426508d51b
- https://git.kernel.org/stable/c/e8adac69d1bdf035ef97cc914e845acd4ef08e28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80663.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80663
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
