# [M] ESP32-audioI2S 3.4.4 through 4.0.0 Heap-based Out-of-Bounds Read via Shadowed Length Parameter in read_ID3_Header

## Summary
Severity: Medium
Advisory: CVE-2026-87961
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-87961
Type: osv

## Details
ESP32-audioI2S versions 3.4.4 through 4.0.0 contain a heap-based out-of-bounds read vulnerability in the read_ID3_Header function due to a shadowed length parameter in ID3 synchronized-lyrics processing. Attackers can craft malicious MP3 files or HTTP audio streams with oversized frame size declarations to read past allocated buffer boundaries, causing device crashes or exposing adjacent heap memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87961.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-87961
- https://www.vulncheck.com/advisories/esp32-audioi2s-3.4.4-through-4.0.0-heap-based-out-of-bounds-read-via-shadowed-length-parameter-in-read-id3-header
- https://github.com/schreibfaul1/ESP32-audioI2S/issues/1380
- https://github.com/schreibfaul1/ESP32-audioI2S/commit/4dc4614b9dab2de7b342d682b1c18b109d75b677
- https://github.com/schreibfaul1/ESP32-audioI2S/pull/1381
- https://github.com/schreibfaul1/ESP32-audioI2S
- https://github.com/schreibfaul1/ESP32-audioI2S/blob/490ff729eca344f06581f3e9bda9cfba948fd5a1/src/Audio.cpp#L2526-L2531
- https://github.com/schreibfaul1/ESP32-audioI2S/blob/490ff729eca344f06581f3e9bda9cfba948fd5a1/src/Audio.cpp#L2629-L2635
- https://github.com/schreibfaul1/ESP32-audioI2S/blob/f01ad7923dcf3355eeca7fb99bf8a4d9945e7478/src/Audio.cpp#L2270-L2276
