# [H] net: mana: Skip redundant detach on already-detached port

## Summary
Severity: High
Advisory: CVE-2026-63972
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63972
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: Skip redundant detach on already-detached port

When mana_per_port_queue_reset_work_handler() runs after a previous
detach succeeded but attach failed, the port is left in a detached
state with apc->tx_qp and apc->rxqs already freed. Calling
mana_detach() again unconditionally leads to NULL pointer dereferences
during queue teardown.

Add an early exit in mana_detach() when the port is already in
detached state (!netif_device_present) for non-close callers, making
it safe to call idempotently. This allows the queue reset handler and
other recovery paths to simply retry mana_attach() without redundant
teardown.

## References
- https://git.kernel.org/stable/c/5b05aa36ee24297d7296ca58dfd8c448d0e4cda3
- https://git.kernel.org/stable/c/7ae590797f9b5c240aaea5773f5f00977a42a846
- https://git.kernel.org/stable/c/c4152b4e28b3e550ec99351bf900e2c24c2608cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63972.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63972
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
