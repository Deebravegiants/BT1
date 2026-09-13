# [C] FreeRDP: Heap buffer overflow in Opus audio decode (`freerdp_dsp_decode_opus` resizes the wrong stream) — server→client

## Summary
Severity: Critical
Advisory: CVE-2026-63633
Aliases: GHSA-72j9-356v-88xq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-63633
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.28.0, freerdp_dsp_decode_opus in libfreerdp/codec/dsp.c calls Stream_EnsureRemainingCapacity on context->common.buffer even though opus_decode writes decoded PCM into the caller-supplied out stream. A malicious RDP server that negotiates WAVE_FORMAT_OPUS with a client built with WITH_OPUS enabled and WITH_DSP_FFMPEG disabled can make libopus write a large decoded frame beyond the 4096-byte StreamPool_Take destination used by channels/rdpsnd/client/rdpsnd_main.c. This can corrupt the client heap, crash the client, and may permit code execution. This issue is fixed in version 3.28.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.28.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63633.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-72j9-356v-88xq
- https://nvd.nist.gov/vuln/detail/CVE-2026-63633
- https://github.com/FreeRDP/FreeRDP/commit/0ed1f95d36913581cf31124f94eb5843d4263eae
- https://github.com/FreeRDP/FreeRDP/pull/12993
