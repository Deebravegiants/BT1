# [M] x86/CPU/AMD: Clear virtualized VMLOAD/VMSAVE on Zen4 client

## Summary
Severity: Medium
Advisory: CVE-2024-53114
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53114
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/CPU/AMD: Clear virtualized VMLOAD/VMSAVE on Zen4 client

A number of Zen4 client SoCs advertise the ability to use virtualized
VMLOAD/VMSAVE, but using these instructions is reported to be a cause
of a random host reboot.

These instructions aren't intended to be advertised on Zen4 client
so clear the capability.

## References
- https://git.kernel.org/stable/c/00c713f84f477a85e524f34aad8fbd11a1c051f0
- https://git.kernel.org/stable/c/a5ca1dc46a6b610dd4627d8b633d6c84f9724ef0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53114.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53114
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
