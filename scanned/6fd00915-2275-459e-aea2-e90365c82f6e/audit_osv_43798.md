# [H] ovpn: defer key slot crypto freeing to workqueue

## Summary
Severity: High
Advisory: CVE-2026-74750
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74750
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: defer key slot crypto freeing to workqueue

Key slots are released through a kref and the existing release path
frees the AEAD transforms from an RCU callback. That is not safe for all
crypto implementations: crypto_free_aead can sleep, for example when an
async or hardware implementation has teardown work to complete.

Use queue_rcu_work for key-slot release. This keeps the RCU grace period
needed by lockless key-slot readers, but runs the actual crypto teardown
from workqueue context where sleeping is allowed. Once the rcu_work
callback runs, pre-existing RCU readers are gone, and the final kref put
already proves that no transform user remains, so the worker can release
the AEAD transforms and free the slot directly.

The previous patch drains ovpn_wq during module exit, so queued key-slot
teardown work cannot outlive module text.

## References
- https://git.kernel.org/stable/c/0f77ed5ee91946ea63e29f2e0ff9dc9e722d8da3
- https://git.kernel.org/stable/c/2da3dfa1ddfe55a065f484750c83660e3bd4ac00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74750.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
