# [M] net: ethernet: ti: am65-cpsw: Fix NAPI registration sequence

## Summary
Severity: Medium
Advisory: CVE-2025-22006
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-22006
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.14 <6.12.21, >=6.13.3 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: ti: am65-cpsw: Fix NAPI registration sequence

Registering the interrupts for TX or RX DMA Channels prior to registering
their respective NAPI callbacks can result in a NULL pointer dereference.
This is seen in practice as a random occurrence since it depends on the
randomness associated with the generation of traffic by Linux and the
reception of traffic from the wire.

## References
- https://git.kernel.org/stable/c/5f079290e5913a0060e059500b7d440990ac1066
- https://git.kernel.org/stable/c/942557abed7f38b77a47d77b92d448802eefe185
- https://git.kernel.org/stable/c/d4bf956547c38c04fad8d72a961ac4dc00bad000
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22006.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22006
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
