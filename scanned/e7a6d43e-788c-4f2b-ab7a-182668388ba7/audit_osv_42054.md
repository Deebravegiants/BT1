# [H] Bluetooth: bnep: pin L2CAP connection during netdev registration

## Summary
Severity: High
Advisory: CVE-2026-64408
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64408
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: bnep: pin L2CAP connection during netdev registration

bnep_add_connection() reads the L2CAP connection without holding the
channel lock, then passes its HCI device to register_netdev(). Controller
teardown can clear and release that connection concurrently, leaving the
network device registration path to dereference a freed parent device.

Take a reference to the L2CAP connection while holding the channel lock.
Retain it until register_netdev() has taken the parent device reference.

## References
- https://git.kernel.org/stable/c/390b5db3ff8745187f094c4e915663b7b1f98944
- https://git.kernel.org/stable/c/46a88784c4c9b96954dd86f747ce93f65efa1302
- https://git.kernel.org/stable/c/551ae773ec64045b4e72099132654887e0270bcc
- https://git.kernel.org/stable/c/563a8573047182f550b1e1e030615755cd8c41da
- https://git.kernel.org/stable/c/a6b22dbd80926556290ad2243be25218d6956a19
- https://git.kernel.org/stable/c/ae215c5b6422d8eda443b861b124bd1be6969c31
- https://git.kernel.org/stable/c/bb067a99a0356196c0b89a95721985485ebce5a5
- https://git.kernel.org/stable/c/df22adc7eafc22e651561813c11dc51a796b12ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64408.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
