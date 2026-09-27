# [H] octeontx2-af: Use separate handlers for interrupts

## Summary
Severity: High
Advisory: CVE-2024-27030
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27030
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: Use separate handlers for interrupts

For PF to AF interrupt vector and VF to AF vector same
interrupt handler is registered which is causing race condition.
When two interrupts are raised to two CPUs at same time
then two cores serve same event corrupting the data.

## References
- https://git.kernel.org/stable/c/29d2550d79a8cbd31e0fbaa5c0e2a2efdc444e44
- https://git.kernel.org/stable/c/4fedae8f9eafa2ac8cdaca58e315f52a7e2a8701
- https://git.kernel.org/stable/c/50e60de381c342008c0956fd762e1c26408f372c
- https://git.kernel.org/stable/c/766c2627acb2d9d1722cce2e24837044d52d888a
- https://git.kernel.org/stable/c/772f18ded0e240cc1fa2b7020cc640e3e5c32b70
- https://git.kernel.org/stable/c/94cb17e5cf3a3c484063abc0ce4b8a2b2e8c1cb2
- https://git.kernel.org/stable/c/ad6759e233db6fcc131055f8e23b4eafbe81053c
- https://git.kernel.org/stable/c/dc29dd00705a62c77de75b6d752259b869aac49d
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27030.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27030
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
