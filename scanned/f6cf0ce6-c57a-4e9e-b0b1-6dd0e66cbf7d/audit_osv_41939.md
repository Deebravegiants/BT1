# [H] Bluetooth: MGMT: validate Add Extended Advertising Data length

## Summary
Severity: High
Advisory: CVE-2026-64126
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64126
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: MGMT: validate Add Extended Advertising Data length

MGMT_OP_ADD_EXT_ADV_DATA is registered as a variable-length command,
with MGMT_ADD_EXT_ADV_DATA_SIZE as the fixed header size.  The handler
then uses cp->adv_data_len and cp->scan_rsp_len to validate and copy
cp->data, but it never checks that those bytes are part of the mgmt
command payload.

A short command can therefore make add_ext_adv_data() pass an
out-of-bounds pointer into tlv_data_is_valid().  If the bytes beyond
the command buffer are addressable, they can also be copied into the
advertising instance as scan response data, where the caller can read
them back via MGMT_OP_GET_ADV_INSTANCE.  The trigger requires
CAP_NET_ADMIN in the initial user namespace; KASAN reports an 8-byte
slab-out-of-bounds read.

Reject commands whose length does not match the fixed header plus both
advertising data lengths before parsing cp->data.

## References
- https://git.kernel.org/stable/c/0bc1a5a69f541859293d79db72bd7854ac48df51
- https://git.kernel.org/stable/c/0d5104390b445e7bd664ad583837e4c04d892c9d
- https://git.kernel.org/stable/c/14b01b9cba04e6ce82825f68fc4c4322fa4ffa43
- https://git.kernel.org/stable/c/a143ce77a5292f2c9285137433d879ce71d190a7
- https://git.kernel.org/stable/c/a6c75a3fad226ccbd8ef9110dee87c92c299f2ab
- https://git.kernel.org/stable/c/d3f7d17960ed50df3a6709c5158caff989c8c905
- https://git.kernel.org/stable/c/f1febe93ef075314615f970a87681d9ab86691d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64126.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64126
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
