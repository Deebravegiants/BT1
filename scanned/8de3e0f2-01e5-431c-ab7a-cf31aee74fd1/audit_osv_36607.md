# [M] FreeRDP has a Heap-buffer-overflow in audio_formats_free

## Summary
Severity: Medium
Advisory: CVE-2026-24682
Aliases: GHSA-vcw2-pqgw-mx6g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24682
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, audin_server_recv_formats frees an incorrect number of audio formats on parse failure (i + i), leading to out-of-bounds access in audio_formats_free. This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24682.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-vcw2-pqgw-mx6g
- https://nvd.nist.gov/vuln/detail/CVE-2026-24682
- https://github.com/FreeRDP/FreeRDP/commit/1c5c74223179d425a1ce6dbbb6a3dd2a958b7aee
