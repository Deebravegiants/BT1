# [H] vfio/pci: Create persistent INTx handler

## Summary
Severity: High
Advisory: CVE-2024-26812
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-05
Source: https://osv.dev/vulnerability/CVE-2024-26812
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/pci: Create persistent INTx handler

A vulnerability exists where the eventfd for INTx signaling can be
deconfigured, which unregisters the IRQ handler but still allows
eventfds to be signaled with a NULL context through the SET_IRQS ioctl
or through unmask irqfd if the device interrupt is pending.

Ideally this could be solved with some additional locking; the igate
mutex serializes the ioctl and config space accesses, and the interrupt
handler is unregistered relative to the trigger, but the irqfd path
runs asynchronous to those.  The igate mutex cannot be acquired from the
atomic context of the eventfd wake function.  Disabling the irqfd
relative to the eventfd registration is potentially incompatible with
existing userspace.

As a result, the solution implemented here moves configuration of the
INTx interrupt handler to track the lifetime of the INTx context object
and irq_type configuration, rather than registration of a particular
trigger eventfd.  Synchronization is added between the ioctl path and
eventfd_signal() wrapper such that the eventfd trigger can be
dynamically updated relative to in-flight interrupts or irqfd callbacks.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0e09cf81959d9f12b75ad5c6dd53d237432ed034
- https://git.kernel.org/stable/c/18c198c96a815c962adc2b9b77909eec0be7df4d
- https://git.kernel.org/stable/c/27d40bf72dd9a6600b76ad05859176ea9a1b4897
- https://git.kernel.org/stable/c/4c089cefe30924fbe20dd1ee92774ea1f5eca834
- https://git.kernel.org/stable/c/4cb0d7532126d23145329826c38054b4e9a05e7c
- https://git.kernel.org/stable/c/69276a555c740acfbff13fb5769ee9c92e1c828e
- https://git.kernel.org/stable/c/7d29d4c72c1e196cce6969c98072a272d1a703b3
- https://git.kernel.org/stable/c/b18fa894d615c8527e15d96b76c7448800e13899
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26812.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26812
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
