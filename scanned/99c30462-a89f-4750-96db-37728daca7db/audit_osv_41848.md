# [C] ipv6: rpl: fix hdrlen overflow in ipv6_rpl_srh_decompress()

## Summary
Severity: Critical
Advisory: CVE-2026-63984
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63984
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: rpl: fix hdrlen overflow in ipv6_rpl_srh_decompress()

ipv6_rpl_srh_decompress() computes:

    outhdr->hdrlen = (((n + 1) * sizeof(struct in6_addr)) >> 3);

hdrlen is __u8. For n >= 127 the result exceeds 255 and silently
truncates. With n=127 (cmpri=15, cmpre=15, pad=0, hdrlen=16):

    (128 * 16) >> 3 = 256, truncated to 0 as __u8

The caller in ipv6_rpl_srh_rcv() then places the compressed header
at buf + ((ohdr->hdrlen + 1) << 3). With hdrlen=0 this is buf + 8,
but the decompressed region occupies buf[0..2055] (8-byte header
plus 128 full addresses). The compressed header overlaps the
decompressed data, and ipv6_rpl_srh_compress() writes into this
overlap, corrupting the routing header of the forwarded packet.

The existing guard at exthdrs.c:546 checks (n + 1) > 255, which
prevents n+1 from overflowing unsigned char (the segments_left
field), but does not prevent the computed hdrlen from overflowing
__u8. n=127 passes because 128 <= 255, yet hdrlen=256 does not
fit.

Tighten the bound to (n + 1) > 127. This caps n at 126, giving
hdrlen = (127 * 16) >> 3 = 254, which fits in __u8. The compressed
header then lands at buf + ((254 + 1) << 3) = buf + 2040, exactly
past the decompressed region (buf[0..2039]). No overlap. 127
segments is well beyond any realistic RPL deployment.

## References
- https://git.kernel.org/stable/c/3618b34942b76471d044369bfd30d58c39068bf1
- https://git.kernel.org/stable/c/6fe1cb312038516cb4d9fa089d700af7059f1a64
- https://git.kernel.org/stable/c/75b3680047bf09af8e7e471a7a6ddf2ce5847f56
- https://git.kernel.org/stable/c/97e06791368c01f0ad2a4b3269c2abe19485ca32
- https://git.kernel.org/stable/c/9d5e7a46a9f6d8f503b41bfefef70659845f1679
- https://git.kernel.org/stable/c/c0487a9c1e116cf349e2d1f302d9019670460858
- https://git.kernel.org/stable/c/de02fc049352af5a9595f015511222d0a85c326b
- https://git.kernel.org/stable/c/fd238c51b0fa5390cceca9f1ac5a9ffda8063eed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63984.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63984
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
