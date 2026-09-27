# [H] bpf: Fix tcx/netkit detach permissions when prog fd isn't given

## Summary
Severity: High
Advisory: CVE-2026-45932
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45932
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix tcx/netkit detach permissions when prog fd isn't given

This commit fixes a security issue where BPF_PROG_DETACH on tcx or
netkit devices could be executed by any user when no program fd was
provided, bypassing permission checks. The fix adds a capability
check for CAP_NET_ADMIN or CAP_SYS_ADMIN in this case.

## References
- https://git.kernel.org/stable/c/3f04cc1e5374da4c5e791ae010a06cfea7bacbe6
- https://git.kernel.org/stable/c/4e0772cded109c238411f2fac36ac39302758b81
- https://git.kernel.org/stable/c/ae23bc81ddf7c17b663c4ed1b21e35527b0a7131
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45932.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45932
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
