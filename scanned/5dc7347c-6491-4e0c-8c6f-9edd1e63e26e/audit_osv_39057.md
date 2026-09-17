# [H] net: wwan: t7xx: validate port_count against message length in t7xx_port_enum_msg_handler

## Summary
Severity: High
Advisory: CVE-2026-43495
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-43495
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: wwan: t7xx: validate port_count against message length in t7xx_port_enum_msg_handler

t7xx_port_enum_msg_handler() uses the modem-supplied port_count field as
a loop bound over port_msg->data[] without checking that the message buffer
contains sufficient data. A modem sending port_count=65535 in a 12-byte
buffer triggers a slab-out-of-bounds read of up to 262140 bytes.

Add a sizeof(*port_msg) check before accessing the port message header
fields to guard against undersized messages.

Add a struct_size() check after extracting port_count and before the loop.

In t7xx_parse_host_rt_data(), guard the rt_feature header read with a
remaining-buffer check before accessing data_len, validate feat_data_len
against the actual remaining buffer to prevent OOB reads and signed
integer overflow on offset.

Pass msg_len from both call sites: skb->len at the DPMAIF path after
skb_pull(), and the validated feat_data_len at the handshake path.

## References
- http://www.openwall.com/lists/oss-security/2026/06/18/1
- https://git.kernel.org/stable/c/0e7c074cfcd9bd93765505f9eb8b42f03ed2a744
- https://git.kernel.org/stable/c/2b56d7903ab804481f5233a259d5f341e9fd513c
- https://git.kernel.org/stable/c/307c5d0f36a5c74042217136da5bfbd9f7504650
- https://git.kernel.org/stable/c/9855e063e063158cc5bded576382599dc3133202
- https://git.kernel.org/stable/c/dd4f4c93c1488d7100b9964f2da4c8b3c29652f1
- https://git.kernel.org/stable/c/f94450ce5053b36002995b72d1fa1db3bb08c5bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43495.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43495
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
