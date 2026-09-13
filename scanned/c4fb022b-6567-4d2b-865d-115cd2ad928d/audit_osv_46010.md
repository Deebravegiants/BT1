# [H] JLSEC-2026-568

## Summary
Severity: High
Advisory: JLSEC-2026-568
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/JLSEC-2026-568
Type: osv

## Affected
- Julia: `OpenCV_jll` — affected >=0 <4.10.0+0

## Details
A vulnerability, which was classified as problematic, has been found in OpenCV `wechat_qrcode` Module up to 4.7.0. Affected by this issue is the function DecodedBitStreamParser::decodeHanziSegment of the file `qrcode/decoder/decoded_bit_stream_parser.cpp`. The manipulation leads to memory leak. The attack may be launched remotely. The name of the patch is 2b62ff6181163eea029ed1cab11363b4996e9cd6. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-228548.

## References
- https://github.com/opencv/opencv_contrib/pull/3484
- https://github.com/opencv/opencv_contrib/pull/3484/commits/2b62ff6181163eea029ed1cab11363b4996e9cd6
- https://vuldb.com/?ctiid.228548
- https://vuldb.com/?id.228548
