# [C] FreeRDP before 3.29.0 Integer Overflow via Audio Input Channel

## Summary
Severity: Critical
Advisory: CVE-2026-68580
Aliases: GHSA-69xf-pqrw-596x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-02
Source: https://osv.dev/vulnerability/CVE-2026-68580
Type: osv

## Details
FreeRDP before 3.29.0 contains integer overflow vulnerabilities in the audio input redirection channel (audin) across ALSA, sndio, WinMM, and OpenSL ES backends that fail to validate the FramesPerPacket parameter from RDP servers. Attackers can supply a malicious FramesPerPacket value causing allocation size wraparound, resulting in heap-based buffer overflow on ALSA or denial of service on all platforms.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68580.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-69xf-pqrw-596x
- https://nvd.nist.gov/vuln/detail/CVE-2026-68580
- https://www.vulncheck.com/advisories/freerdp-before-integer-overflow-via-audio-input-channel
