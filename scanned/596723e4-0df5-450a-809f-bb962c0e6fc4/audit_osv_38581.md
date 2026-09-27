# [C] PJSIP: Heap buffer overflow in Opus codec decoding

## Summary
Severity: Critical
Advisory: CVE-2026-40614
Aliases: GHSA-j59p-4xrr-fp8g
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40614
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. In 2.16 and earlier, there is a buffer overflow when decoding Opus audio frames due to insufficient buffer size validation in the Opus codec decode path. The FEC decode buffers (dec_frame[].buf) were allocated based on a PCM-derived formula: (sample_rate/1000) * 60 * channel_cnt * 2. At 8 kHz mono this yields only 960 bytes, but codec_parse() can output encoded frames up to MAX_ENCODED_PACKET_SIZE (1280) bytes via opus_repacketizer_out_range(). The three pj_memcpy() calls in codec_decode() copied input->size bytes without bounds checking, causing a heap buffer overflow.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40614.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-j59p-4xrr-fp8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-40614
- https://github.com/pjsip/pjproject/commit/17897e835818f8ee03b1806ddcd7b95ea16d2c0e
