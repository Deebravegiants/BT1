# [H] tun: add missing verification for short frame

## Summary
Severity: High
Advisory: CVE-2024-41091
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41091
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.102, >=6.2.0 <6.6.43, >=6.7.0 <6.9.12, >=6.10.0 <6.10.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

tun: add missing verification for short frame

The cited commit missed to check against the validity of the frame length
in the tun_xdp_one() path, which could cause a corrupted skb to be sent
downstack. Even before the skb is transmitted, the
tun_xdp_one-->eth_type_trans() may access the Ethernet header although it
can be less than ETH_HLEN. Once transmitted, this could either cause
out-of-bound access beyond the actual length, or confuse the underlayer
with incorrect or inconsistent header length in the skb metadata.

In the alternative path, tun_get_user() already prohibits short frame which
has the length less than Ethernet header size from being transmitted for
IFF_TAP.

This is to drop any frame shorter than the Ethernet header size just like
how tun_get_user() does.

CVE: CVE-2024-41091

## References
- https://git.kernel.org/stable/c/049584807f1d797fc3078b68035450a9769eb5c3
- https://git.kernel.org/stable/c/32b0aaba5dbc85816898167d9b5d45a22eae82e9
- https://git.kernel.org/stable/c/589382f50b4a5d90d16d8bc9dcbc0e927a3e39b2
- https://git.kernel.org/stable/c/6100e0237204890269e3f934acfc50d35fd6f319
- https://git.kernel.org/stable/c/8418f55302fa1d2eeb73e16e345167e545c598a5
- https://git.kernel.org/stable/c/a9d1c27e2ee3b0ea5d40c105d6e728fc114470bb
- https://git.kernel.org/stable/c/ad6b3f622ccfb4bfedfa53b6ebd91c3d1d04f146
- https://git.kernel.org/stable/c/d5ad89b7d01ed4e66fd04734fc63d6e78536692a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41091.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41091
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
