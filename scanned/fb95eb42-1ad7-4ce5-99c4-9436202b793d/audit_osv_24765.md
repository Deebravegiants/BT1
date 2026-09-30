# [M] OpenCV wechat_qrcode Module decoded_bit_stream_parser.cpp decodeHanziSegment memory leak

## Summary
Severity: Medium
Advisory: CVE-2023-2618
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-05-10
Source: https://osv.dev/vulnerability/CVE-2023-2618
Type: osv

## Details
A vulnerability, which was classified as problematic, has been found in OpenCV wechat_qrcode Module up to 4.7.0. Affected by this issue is the function DecodedBitStreamParser::decodeHanziSegment of the file qrcode/decoder/decoded_bit_stream_parser.cpp. The manipulation leads to memory leak. The attack may be launched remotely. The name of the patch is 2b62ff6181163eea029ed1cab11363b4996e9cd6. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-228548.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2618.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2618
- https://vuldb.com/?id.228548
- https://github.com/opencv/opencv_contrib/pull/3484
- https://vuldb.com/?ctiid.228548
- https://github.com/opencv/opencv_contrib/pull/3484/commits/2b62ff6181163eea029ed1cab11363b4996e9cd6
