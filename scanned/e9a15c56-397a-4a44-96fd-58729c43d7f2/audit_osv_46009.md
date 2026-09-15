# [H] JLSEC-2026-567

## Summary
Severity: High
Advisory: JLSEC-2026-567
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/JLSEC-2026-567
Type: osv

## Affected
- Julia: `OpenCV_jll` — affected >=0 <4.10.0+0

## Details
A vulnerability classified as problematic was found in OpenCV `wechat_qrcode` Module up to 4.7.0. Affected by this vulnerability is the function DecodedBitStreamParser::decodeByteSegment of the file `qrcode/decoder/decoded_bit_stream_parser.cpp`. The manipulation leads to null pointer dereference. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-228547.

## References
- https://gist.github.com/GZTimeWalker/3ca70a8af2f5830711e9cccc73fb5270
- https://github.com/opencv/opencv_contrib/pull/3480
- https://vuldb.com/?ctiid.228547
- https://vuldb.com/?id.228547
