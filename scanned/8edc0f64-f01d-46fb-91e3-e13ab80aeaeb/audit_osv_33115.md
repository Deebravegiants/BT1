# [M] media: venus: protect against spurious interrupts during probe

## Summary
Severity: Medium
Advisory: CVE-2025-39709
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39709
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: protect against spurious interrupts during probe

Make sure the interrupt handler is initialized before the interrupt is
registered.

If the IRQ is registered before hfi_create(), it's possible that an
interrupt fires before the handler setup is complete, leading to a NULL
dereference.

This error condition has been observed during system boot on Rb3Gen2.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/18c2b2bd982b8546312c9a7895515672169f28e0
- https://git.kernel.org/stable/c/3200144a2fa4209dc084a19941b9b203b43580f0
- https://git.kernel.org/stable/c/37cc0ac889b018097c217c5929fd6dc2aed636a1
- https://git.kernel.org/stable/c/639eb587f977c02423f4762467055b23902b4131
- https://git.kernel.org/stable/c/88cf63c2599761c48dec8f618d57dccf8f6f4b53
- https://git.kernel.org/stable/c/9db6a78bc5e418e0064e2248c8f3b9b9e8418646
- https://git.kernel.org/stable/c/e796028b4835af00d9a38ebbb208ec3a6634702a
- https://git.kernel.org/stable/c/f54be97bc69b1096198b6717c150dec69f2a1b4d
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39709.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39709
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
