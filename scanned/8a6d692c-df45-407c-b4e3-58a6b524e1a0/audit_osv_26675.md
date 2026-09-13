# [H] net: bcmgenet: Add a check for oversized packets

## Summary
Severity: High
Advisory: CVE-2023-53535
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53535
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bcmgenet: Add a check for oversized packets

Occasionnaly we may get oversized packets from the hardware which
exceed the nomimal 2KiB buffer size we allocate SKBs with. Add an early
check which drops the packet to avoid invoking skb_over_panic() and move
on to processing the next packet.

## References
- https://git.kernel.org/stable/c/124ca24e0de958d2e20e0aa1e2434af7b72f8887
- https://git.kernel.org/stable/c/411317d2a4a7d6049d8efeef0d32ae43f8baefce
- https://git.kernel.org/stable/c/5c0862c2c962052ed5055220a00ac1cefb92fbcd
- https://git.kernel.org/stable/c/5f56767fb5f2df875b6553e08dbec6a45431c988
- https://git.kernel.org/stable/c/7cdb07e10c1258c08f31b24898930e4ece88d163
- https://git.kernel.org/stable/c/841881320562cbeac7046b537b91cd000480cea2
- https://git.kernel.org/stable/c/87363d1ab55e497702a9506ff423c422639c8a25
- https://git.kernel.org/stable/c/c34b1c0870323649d45c5074828d7f754dea2673
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53535.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53535
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
