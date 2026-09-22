# [H] Suricata's mishandling of data on  HTTP2 stream 0 can lead to resource starvation

## Summary
Severity: High
Advisory: CVE-2025-53538
Aliases: GHSA-qrr7-crgj-cmh3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-53538
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. In versions 7.0.10 and below and  8.0.0-beta1 through 8.0.0-rc1, mishandling of data on HTTP2 stream 0 can lead to uncontrolled memory usage, leading to loss of visibility. Workarounds include disabling the HTTP/2 parser, and using a signature like drop http2 any any -> any any (frame:http2.hdr; byte_test:1,=,0,3; byte_test:4,=,0,5; sid: 1;) where the first byte test tests the HTTP2 frame type DATA and the second tests the stream id 0. This is fixed in versions 7.0.11 and 8.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53538.json
- https://github.com/OISF/suricata/security/advisories/GHSA-qrr7-crgj-cmh3
- https://nvd.nist.gov/vuln/detail/CVE-2025-53538
- https://github.com/OISF/suricata/commit/1d6d331752e933c46aca0ae7a9679b27462246e3
- https://github.com/OISF/suricata/commit/7fa88ea9e7d05e07a7864050cfd836b576669720
