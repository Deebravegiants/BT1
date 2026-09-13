# [H] vfio/pci: Lock external INTx masking ops

## Summary
Severity: High
Advisory: CVE-2024-26810
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-05
Source: https://osv.dev/vulnerability/CVE-2024-26810
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/pci: Lock external INTx masking ops

Mask operations through config space changes to DisINTx may race INTx
configuration changes via ioctl.  Create wrappers that add locking for
paths outside of the core interrupt code.

In particular, irq_type is updated holding igate, therefore testing
is_intx() requires holding igate.  For example clearing DisINTx from
config space can otherwise race changes of the interrupt configuration.

This aligns interfaces which may trigger the INTx eventfd into two
camps, one side serialized by igate and the other only enabled while
INTx is configured.  A subsequent patch introduces synchronization for
the latter flows.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/03505e3344b0576fd619416793a31eae9c5b73bf
- https://git.kernel.org/stable/c/04a4a017b9ffd7b0f427b8c376688d14cb614651
- https://git.kernel.org/stable/c/1e71b6449d55179170efc8dee8664510bb813b42
- https://git.kernel.org/stable/c/3dd9be6cb55e0f47544e7cdda486413f7134e3b3
- https://git.kernel.org/stable/c/3fe0ac10bd117df847c93408a9d428a453cd60e5
- https://git.kernel.org/stable/c/6fe478d855b20ac1eb5da724afe16af5a2aaaa40
- https://git.kernel.org/stable/c/810cd4bb53456d0503cc4e7934e063835152c1b7
- https://git.kernel.org/stable/c/ec73e079729258a05452356cf6d098bf1504d5a6
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26810.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26810
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
