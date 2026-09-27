# [M] FreeRDP has a Heap-use-after-free in play_thread

## Summary
Severity: Medium
Advisory: CVE-2026-24684
Aliases: GHSA-vcgv-xgjp-h83q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24684
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, the RDPSND async playback thread can process queued PDUs after the channel is closed and internal state is freed, leading to a use after free in rdpsnd_treat_wave. This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24684.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-vcgv-xgjp-h83q
- https://nvd.nist.gov/vuln/detail/CVE-2026-24684
- https://github.com/FreeRDP/FreeRDP/commit/622bb7b4402491ca003f47472d0e478132673696
- https://github.com/FreeRDP/FreeRDP/commit/afa6851dc80835d3101e40fcef51b6c5c0f43ea5
