# [H] ovpn: fix use after free in unlock_ovpn()

## Summary
Severity: High
Advisory: CVE-2026-68341
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68341
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: fix use after free in unlock_ovpn()

unlock_ovpn() iterates over the release_list using llist_for_each_entry()
and drops the peer reference inside the loop body via ovpn_peer_put().

If this drops the last reference, the peer is eventually freed. However,
llist_for_each_entry() reads peer->release_entry.next in the loop advance
expression, which runs after the body. By that time the peer may have
already been freed, resulting in a use after free when advancing to the
next list entry.

Fix this by using llist_for_each_entry_safe(), which caches the next
pointer before executing the loop body.

## References
- https://git.kernel.org/stable/c/4cdb209f12a89c5faf9be0c45edb90ccdf65db0c
- https://git.kernel.org/stable/c/5b96227c0e8b212b74838424c929fc889aedb555
- https://git.kernel.org/stable/c/e1ad6fe5db719874efa45b2caf9934552e09fc43
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68341.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68341
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
