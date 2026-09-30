# [H] Bluetooth: L2CAP: Fix type confusion in l2cap_ecred_reconf_rsp()

## Summary
Severity: High
Advisory: CVE-2026-43062
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-43062
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: Fix type confusion in l2cap_ecred_reconf_rsp()

l2cap_ecred_reconf_rsp() casts the incoming data to struct
l2cap_ecred_conn_rsp (the ECRED *connection* response, 8 bytes with
result at offset 6) instead of struct l2cap_ecred_reconf_rsp (2 bytes
with result at offset 0).

This causes two problems:

 - The sizeof(*rsp) length check requires 8 bytes instead of the
   correct 2, so valid L2CAP_ECRED_RECONF_RSP packets are rejected
   with -EPROTO.

 - rsp->result reads from offset 6 instead of offset 0, returning
   wrong data when the packet is large enough to pass the check.

Fix by using the correct type.  Also pass the already byte-swapped
result variable to BT_DBG instead of the raw __le16 field.

## References
- https://git.kernel.org/stable/c/111f74547eee8cfedfb854284e80f35c8a491186
- https://git.kernel.org/stable/c/15145675690cab2de1056e7ed68e59cbd0452529
- https://git.kernel.org/stable/c/21d3ba696918d6373233aac0b9d51fcabdedddc0
- https://git.kernel.org/stable/c/3b94e62caa1dc1198d0d55d97bd710da1dee15d7
- https://git.kernel.org/stable/c/5a1ea296f8589ce8f1e3141b2b123b34ad010e19
- https://git.kernel.org/stable/c/d90150c72d2e6a8a3079e88755dafcfbe91c746d
- https://git.kernel.org/stable/c/dd3b221e21079ade8263fbb7176f3d55ad75d3b6
- https://git.kernel.org/stable/c/f110b8f58b254bf997cec1bd60701b7798e9bb82
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43062.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43062
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
