# [H] ipvs: Defer ip_vs_ftp unregister during netns cleanup

## Summary
Severity: High
Advisory: CVE-2025-40018
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-24
Source: https://osv.dev/vulnerability/CVE-2025-40018
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: Defer ip_vs_ftp unregister during netns cleanup

On the netns cleanup path, __ip_vs_ftp_exit() may unregister ip_vs_ftp
before connections with valid cp->app pointers are flushed, leading to a
use-after-free.

Fix this by introducing a global `exiting_module` flag, set to true in
ip_vs_ftp_exit() before unregistering the pernet subsystem. In
__ip_vs_ftp_exit(), skip ip_vs_ftp unregister if called during netns
cleanup (when exiting_module is false) and defer it to
__ip_vs_cleanup_batch(), which unregisters all apps after all connections
are flushed. If called during module exit, unregister ip_vs_ftp
immediately.

## References
- https://git.kernel.org/stable/c/134121bfd99a06d44ef5ba15a9beb075297c0821
- https://git.kernel.org/stable/c/1d79471414d7b9424d699afff2aa79fff322f52d
- https://git.kernel.org/stable/c/421b1ae1574dfdda68b835c15ac4921ec0030182
- https://git.kernel.org/stable/c/53717f8a4347b78eac6488072ad8e5adbaff38d9
- https://git.kernel.org/stable/c/8a6ecab3847c213ce2855b0378e63ce839085de3
- https://git.kernel.org/stable/c/8cbe2a21d85727b66d7c591fd5d83df0d8c4f757
- https://git.kernel.org/stable/c/a343811ef138a265407167294275201621e9ebb2
- https://git.kernel.org/stable/c/dc1a481359a72ee7e548f1f5da671282a7c13b8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40018.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40018
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
