# [C] ksmbd: not allow guest user on multichannel

## Summary
Severity: Critical
Advisory: CVE-2023-32249
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2023-32249
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.112, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: not allow guest user on multichannel

This patch return STATUS_NOT_SUPPORTED if binding session is guest.

## References
- https://git.kernel.org/stable/c/088131b7b01099720a528a72005ff17868705d40
- https://git.kernel.org/stable/c/1f0490586544455e5be698be2e6c30077b4ec461
- https://git.kernel.org/stable/c/3353ab2df5f68dab7da8d5ebb427a2d265a1f2b2
- https://git.kernel.org/stable/c/4a98e859c4673013385a54084e0cd865695ca072
- https://git.kernel.org/stable/c/ed76d3a8910be06cd4e4ba63bf6075bf903945a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32249.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32249
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
