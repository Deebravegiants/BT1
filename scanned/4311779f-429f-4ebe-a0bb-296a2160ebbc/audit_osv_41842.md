# [H] Bluetooth: L2CAP: Fix possible crash on l2cap_ecred_conn_rsp

## Summary
Severity: High
Advisory: CVE-2026-63975
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63975
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: Fix possible crash on l2cap_ecred_conn_rsp

If dcid is received for an already-assigned destination CID the spec
requires that both channels to be discarded, but calling l2cap_chan_del
may invalidate the tmp cursor created by list_for_each_entry_safe and
in fact it is the wrong procedure as the chan->dcid may be assigned
previously it really needs to be disconnected.

Calling l2cap_chan_clone directly may still lead to l2cap_chan_del so
instead schedule l2cap_chan_timeout with delay 0 to close the channel
asynchronously.

## References
- https://git.kernel.org/stable/c/291eec1041c918c460dc9702e44edd17794b4a4b
- https://git.kernel.org/stable/c/3c8eaa91eb433c450426539290be4ffe282e9f00
- https://git.kernel.org/stable/c/41c2713b204e6cb6a94587bc6bf6935107df5479
- https://git.kernel.org/stable/c/41e29548b5e8b5e5fcf708786b3bea67cab107fa
- https://git.kernel.org/stable/c/6319b38fe69f56ed95680ade485b957a53fff642
- https://git.kernel.org/stable/c/d153b8898c0051eb8b6a083b35cbe304a5886bd5
- https://git.kernel.org/stable/c/e6833e737a51db1e5ea0401322acf5e22abd8be6
- https://git.kernel.org/stable/c/ecfed1e0d8efecad6737a0d83e21d2fd021d8c48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63975.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63975
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
