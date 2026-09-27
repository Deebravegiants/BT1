# [C] net: mana: Validate the packet length reported by the NIC

## Summary
Severity: Critical
Advisory: CVE-2026-72065
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72065
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: Validate the packet length reported by the NIC

Validate the packet length reported in the RX CQE before passing it
to skb processing. The CQE is supplied by the NIC device and should
not be blindly trusted.

## References
- https://git.kernel.org/stable/c/282c5214ca4eb3799158c76782646e86d2945d1b
- https://git.kernel.org/stable/c/2e276b14b6d378372bf0152df89286cbe7632fb0
- https://git.kernel.org/stable/c/2e2a83b4998af4384e677d3b2ac08565274279bf
- https://git.kernel.org/stable/c/6080189291d958604dcefe513a13900835ac982f
- https://git.kernel.org/stable/c/6d13eaa13341a8f80aaf86f78591e1b1d393711d
- https://git.kernel.org/stable/c/a631f82f89c76084ad5b2b9c043d3b391ffa56d8
- https://git.kernel.org/stable/c/d2568e64d01f480200063fadd67d6938f676c66f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72065.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72065
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
