# [H] ieee802154: admin-gate legacy LLSEC dump operations

## Summary
Severity: High
Advisory: CVE-2026-72049
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72049
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ieee802154: admin-gate legacy LLSEC dump operations

In net/ieee802154/netlink.c, the legacy IEEE802154_NL family ops table
builds the LLSEC dump entries (LLSEC_LIST_KEY, LLSEC_LIST_DEV,
LLSEC_LIST_DEVKEY, LLSEC_LIST_SECLEVEL) with IEEE802154_DUMP() which
sets no .flags, so generic netlink runs them ungated. The modern
nl802154 family admin-gates the equivalent reads via
NL802154_CMD_GET_SEC_KEY and friends with .flags = GENL_ADMIN_PERM.

Any local uid that can open AF_NETLINK / NETLINK_GENERIC can resolve
the "802.15.4 MAC" family and dump LLSEC_LIST_KEY on any wpan netdev
that has an LLSEC key installed; the dump handler writes the raw
16-byte AES-128 key bytes (IEEE802154_ATTR_LLSEC_KEY_BYTES, copied
verbatim from struct ieee802154_llsec_key.key) into the reply.
Recovering the AES key compromises 802.15.4 LLSEC link confidentiality
and authenticity, since LLSEC uses CCM* and the same key authenticates
and encrypts frames.

Impact: any local uid with no capabilities can read the raw 16-byte
AES-128 LLSEC key from the kernel keytable on any wpan netdev that has
an administrator-installed LLSEC key, by issuing an LLSEC_LIST_KEY
dump on the legacy IEEE802154_NL generic-netlink family.

Introduce IEEE802154_DUMP_PRIV() mirroring IEEE802154_DUMP() but
setting .flags = GENL_ADMIN_PERM, and use it for the four LLSEC dump
entries. LIST_PHY and LIST_IFACE retain IEEE802154_DUMP() because the
modern nl802154 family exposes their equivalents to unprivileged
readers by design (NL802154_CMD_GET_WPAN_PHY and
NL802154_CMD_GET_INTERFACE carry "can be retrieved by unprivileged
users" annotations).

## References
- https://git.kernel.org/stable/c/09fd25cd8cd80a6b3edef04e53a7324d06ac2180
- https://git.kernel.org/stable/c/1905ebabe638c946aced00c4bb664da26cac56d5
- https://git.kernel.org/stable/c/3465035ba18b1ed50f8d201897d14135d20532b0
- https://git.kernel.org/stable/c/5abe94a205539d27945cda3ba43fdcfe295cf2c8
- https://git.kernel.org/stable/c/6383248058956f2a52d720b1e9f8921099cdae04
- https://git.kernel.org/stable/c/9c1e0b6d49471a712511d23fc9d06901561135e8
- https://git.kernel.org/stable/c/dffe745760f38fac0b8288e0dc4759b23d9888ff
- https://git.kernel.org/stable/c/e84708ef7521f3bffc85a449954042018abbd60e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72049.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72049
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
