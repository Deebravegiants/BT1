# [M] Bluetooth: Add check for mgmt_alloc_skb() in mgmt_device_connected()

## Summary
Severity: Medium
Advisory: CVE-2025-21936
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21936
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Add check for mgmt_alloc_skb() in mgmt_device_connected()

Add check for the return value of mgmt_alloc_skb() in
mgmt_device_connected() to prevent null pointer dereference.

## References
- https://git.kernel.org/stable/c/7841180342c9a0fd97d54f3e62c7369309b5cd84
- https://git.kernel.org/stable/c/7d39387886ffe220323cbed5c155233c3276926b
- https://git.kernel.org/stable/c/bdb1805c248e9694dbb3ffa8867cef2e52cf7261
- https://git.kernel.org/stable/c/d8df010f72b8a32aaea393e36121738bb53ed905
- https://git.kernel.org/stable/c/dc516e66fb28c61b248b393e2ddd63bd7f104969
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21936.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21936
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
