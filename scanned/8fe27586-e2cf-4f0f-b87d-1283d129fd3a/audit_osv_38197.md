# [H] ZLMediaKit VP9 RTP Parser Out-of-Bounds Read

## Summary
Severity: High
Advisory: CVE-2026-35203
Aliases: GHSA-gxr3-fwc7-q99h
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35203
Type: osv

## Details
ZLMediaKit is a streaming media service framework. the VP9 RTP payload parser in ext-codec/VP9Rtp.cpp reads multiple fields from the RTP payload based on flag bits in the first byte, without verifying that sufficient data exists in the buffer. A crafted VP9 RTP packet with a 1-byte payload (0xFF, all flags set) causes the parser to read past the end of the allocated buffer, resulting in a heap-buffer-overflow. This vulnerability is fixed with commit 435dcbcbbf700fd63b2ca9eac6cef3b5ea75169d.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35203.json
- https://github.com/ZLMediaKit/ZLMediaKit/security/advisories/GHSA-gxr3-fwc7-q99h
- https://nvd.nist.gov/vuln/detail/CVE-2026-35203
- https://github.com/ZLMediaKit/ZLMediaKit/commit/435dcbcbbf700fd63b2ca9eac6cef3b5ea75169d
