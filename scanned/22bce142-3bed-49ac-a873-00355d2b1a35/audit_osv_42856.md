# [H] mac802154: remove interfaces with RCU list deletion

## Summary
Severity: High
Advisory: CVE-2026-72024
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72024
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac802154: remove interfaces with RCU list deletion

Queue wake, stop, and disable paths walk local->interfaces under RCU.
The bulk hardware teardown path removes entries with list_del(), so an
asynchronous transmit completion can follow a poisoned list node in
ieee802154_wake_queue().

Use list_del_rcu() as in the single-interface removal path. The following
unregister_netdevice() waits for in-flight RCU readers before freeing the
netdevice, so no separate grace-period wait is needed.

## References
- https://git.kernel.org/stable/c/2039f27b1a0c997137a5de7f8a3cee0e80fbf952
- https://git.kernel.org/stable/c/4bf231f459b542414629b64f63d5cad6701bd07c
- https://git.kernel.org/stable/c/539dfcf69105d8d3d4d677b71de6e5ede2e6dfa0
- https://git.kernel.org/stable/c/72ac5af9ad09662bd0ea91cb8845d490c8ef9c01
- https://git.kernel.org/stable/c/77caf2d6eba7cb94a7ecd7b369a5974fd7d7c054
- https://git.kernel.org/stable/c/b91e5248dd7af09b500879a46d22a36b60db3a57
- https://git.kernel.org/stable/c/c7c031b75218b3ba3014a0f6b9849888994528d6
- https://git.kernel.org/stable/c/d8b5b66388a51febe4b8505b0ecd9da15b4ba639
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72024.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72024
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
