# [C] ovpn: finish crypto callback cleanup before peer release

## Summary
Severity: Critical
Advisory: CVE-2026-80519
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80519
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: finish crypto callback cleanup before peer release

Crypto completion callbacks hold both key-slot and peer references. The
peer reference pins the netdev, and dropping the last peer reference can
let netdev unregistration and module removal make progress.

Do not release that peer reference before the callback has finished its
own cleanup. If ovpn_crypto_key_slot_put runs after ovpn_peer_put, it can
schedule an RCU callback backed by module text after ovpn_cleanup
rcu_barrier has already run. The TX error path also freed the remaining
skb after ovpn_peer_put, leaving callback cleanup outside the peer/netdev
lifetime window.

Release the key slot and free any remaining skb first, then drop the peer
reference as the last callback action.

## References
- https://git.kernel.org/stable/c/4b0de8be288f5fbec5d8ee64ed4e8b14bf19b517
- https://git.kernel.org/stable/c/9e163917a86c6adfbe150e13f4c73653a54616de
- https://git.kernel.org/stable/c/a3a676495c6419e0cca04d6a67227604e92a3d5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80519.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80519
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
