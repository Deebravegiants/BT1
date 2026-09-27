# [H] batman-adv: stop caching unowned originator pointers in BAT IV

## Summary
Severity: High
Advisory: CVE-2026-46238
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46238
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: stop caching unowned originator pointers in BAT IV

BAT IV keeps the last-hop neighbor address in each neigh_node, but some
paths also cache an originator pointer derived from a temporary lookup.
That pointer is not owned by the neigh_node and may no longer refer to a
live originator entry after purge handling runs.

Stop storing the auxiliary originator pointer in the BAT IV neighbor
state. When BAT IV needs the neighbor originator data, resolve it from
the stored neighbor address and drop the reference again after use.

[sven: avoid bonding logic for outgoing OGM]

## References
- https://git.kernel.org/stable/c/09dc0d1a12222ffca6481916eab3cfea477b9620
- https://git.kernel.org/stable/c/384e3050a42be9085d50507b4d5f8266a588d742
- https://git.kernel.org/stable/c/67bceeb22207f1f5a402973a3a0809e5f2698f38
- https://git.kernel.org/stable/c/6e20700f8c524ac379ba8274ff5d453023b7c006
- https://git.kernel.org/stable/c/86b2b58d7c228d850c8c78e4144e6123e8ed2718
- https://git.kernel.org/stable/c/8c16c68fdbb69778f8d04f650340c3f4d1518f8e
- https://git.kernel.org/stable/c/aafcbaf1159ea224528ca4075d0ba8c10ef374af
- https://git.kernel.org/stable/c/f03e8583532941b07761c5429de7d50766fa3110
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46238.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46238
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
