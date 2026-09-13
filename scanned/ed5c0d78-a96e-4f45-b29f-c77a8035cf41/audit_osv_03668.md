# [H] ALPINE-CVE-2026-40614

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-40614
Ecosystem: Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40614
Type: osv

## Affected
- Alpine:v3.24: `pjproject` — affected >=0 <2.17-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. In 2.16 and earlier, there is a buffer overflow when decoding Opus audio frames due to insufficient buffer size validation in the Opus codec decode path. The FEC decode buffers (dec_frame[].buf) were allocated based on a PCM-derived formula: (sample_rate/1000) * 60 * channel_cnt * 2. At 8 kHz mono this yields only 960 bytes, but codec_parse() can output encoded frames up to MAX_ENCODED_PACKET_SIZE (1280) bytes via opus_repacketizer_out_range(). The three pj_memcpy() calls in codec_decode() copied input->size bytes without bounds checking, causing a heap buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40614
