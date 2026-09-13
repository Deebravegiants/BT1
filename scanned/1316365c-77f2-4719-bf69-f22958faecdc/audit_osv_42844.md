# [M] Belledonne Communications bcg729 1.1.2 Out-of-Bounds Read via decodeSIDframe()

## Summary
Severity: Medium
Advisory: CVE-2026-71980
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-71980
Type: osv

## Details
Belledonne Communications bcg729 through 1.1.2 contains an out-of-bounds read vulnerability in the decodeSIDframe() function in src/cng.c that allows unauthenticated network-adjacent attackers to trigger a heap read beyond buffer boundaries by sending a zero-length comfort-noise RTP payload. A zero-length payload causes an integer underflow in the uint8_t filter order calculation, which wraps to 255 and is clamped to 10, causing the function to unconditionally read 11 bytes from a zero-byte buffer, resulting in media process termination or silent consumption of adjacent heap memory as reflection coefficients.

## References
- https://www.linphone.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71980.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71980
- https://www.vulncheck.com/advisories/belledonne-communications-bcg729-out-of-bounds-read-via-decodesidframe
- https://github.com/BelledonneCommunications/bcg729/issues/23
- https://github.com/BelledonneCommunications/bcg729
