# [H] security/keys: fix missed RCU read section on lookup

## Summary
Severity: High
Advisory: CVE-2026-64015
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64015
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

security/keys: fix missed RCU read section on lookup

Nicholas Carlini reports that the keyring code calls assoc_array_find()
in find_key_to_update() without holding the RCU read lock, while the
assoc_array_gc() code really is designed around removing the node from
the tree and then freeing it after an RCU grace-period.

The regular key handling doesn't see this because holding the keyring
semaphore hides any lifetime issues, but the persistent key handling
uses a different model.

Instead of extending the keyring locking, just do the simple RCU locking
that the assoc_array was designed for.

## References
- https://git.kernel.org/stable/c/43a1e3744548e6fd85873e6fb43e293eb4010694
- https://git.kernel.org/stable/c/4c5d407ba3ff7f30561ff73ba1b07ed70c864edc
- https://git.kernel.org/stable/c/50bb3435a5e627bfbdc52eb4536f49f88b3486b8
- https://git.kernel.org/stable/c/5659e6923cb72f8e18e8b539109ab512455fe195
- https://git.kernel.org/stable/c/66288dcadf80974436250e9f70ed848836b835b5
- https://git.kernel.org/stable/c/cefa4265b11176c897a7d9e8e54d89e3701c5584
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64015.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64015
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
