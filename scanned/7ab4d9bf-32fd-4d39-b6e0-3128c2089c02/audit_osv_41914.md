# [H] batman-adv: tt: fix negative tt_buff_len

## Summary
Severity: High
Advisory: CVE-2026-64088
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64088
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: tt: fix negative tt_buff_len

batadv_orig_node::tt_buff_len was declared as s16, but the field is never
intended to hold a negative value. When a value greater than 32767 is
assigned, it wraps to a negative signed integer.

In batadv_send_other_tt_response(), tt_buff_len is temporarily widened to
s32. The incorrectly negative s16 value propagates into the s32, causing
batadv_tt_prepare_tvlv_global_data() to allocate a full sized buffer but
populates only a small portion of it with the collected changeset. All
remaining bits are kept uninitialized.

Using an u16 avoids this type confusion and ensures that no (negative) sign
extension is performed in batadv_send_other_tt_response().

## References
- https://git.kernel.org/stable/c/32edd2a28e112064020a2f319a8cb8a9e5a09767
- https://git.kernel.org/stable/c/33e5ede7ce6d92e531920d4bbd6d3e18ef1c6430
- https://git.kernel.org/stable/c/3c96dff00998314983b68a3e7caac07a66ebe496
- https://git.kernel.org/stable/c/4c4c2f340f4c27373bfcac8dc5032ce7bb474e47
- https://git.kernel.org/stable/c/4dab98961426d0cf6a1599cda6950b7596ca2fcd
- https://git.kernel.org/stable/c/730de8733dd90f70d7580a9b329b971f8e1474a2
- https://git.kernel.org/stable/c/b64963a2ceeb7529310b6cf253a1e540784422f4
- https://git.kernel.org/stable/c/ed28ead3420c373a7928622f114bc6168075d1e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64088.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64088
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
