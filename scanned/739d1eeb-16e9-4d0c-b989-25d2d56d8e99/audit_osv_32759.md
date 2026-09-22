# [H] KVM: x86: Reset IRTE to host control if *new* route isn't postable

## Summary
Severity: High
Advisory: CVE-2025-37885
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37885
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.136, >=6.2.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Reset IRTE to host control if *new* route isn't postable

Restore an IRTE back to host control (remapped or posted MSI mode) if the
*new* GSI route prevents posting the IRQ directly to a vCPU, regardless of
the GSI routing type.  Updating the IRTE if and only if the new GSI is an
MSI results in KVM leaving an IRTE posting to a vCPU.

The dangling IRTE can result in interrupts being incorrectly delivered to
the guest, and in the worst case scenario can result in use-after-free,
e.g. if the VM is torn down, but the underlying host IRQ isn't freed.

## References
- https://git.kernel.org/stable/c/023816bd5fa46fab94d1e7917fe131b79ed1fb41
- https://git.kernel.org/stable/c/116c7d35b8f72eac383b9fd371d7c1a8ffc2968b
- https://git.kernel.org/stable/c/3066ec21d1a33896125747f68638725f456308db
- https://git.kernel.org/stable/c/3481fd96d801715942b6f69fe251133128156f30
- https://git.kernel.org/stable/c/9bcac97dc42d2f4da8229d18feb0fe2b1ce523a2
- https://git.kernel.org/stable/c/b5de7ac74f69603ad803c524b840bffd36368fc3
- https://git.kernel.org/stable/c/e5f2dee9f7fcd2ff4b97869f3c66a0d89c167769
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37885.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37885
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
