# [M] Genymobile/scrcpy <= 3.3.3 Global Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2025-34449
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-34449
Type: osv

## Details
Genymobile/scrcpy versions up to and including 3.3.3, prior to commit 3e40b24, contain a buffer overflow vulnerability in the sc_device_msg_deserialize() function. A compromised device can send crafted messages that cause out-of-bounds reads, which may result in memory corruption or a denial-of-service condition. This vulnerability may allow further exploitation on the host system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34449.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34449
- https://www.vulncheck.com/advisories/genymobile-scrcpy-global-buffer-overflow
- https://github.com/Genymobile/scrcpy/issues/6415
- https://github.com/Genymobile/scrcpy/commit/3e40b24
- https://github.com/Genymobile/scrcpy
- https://github.com/marlinkcyber/advisories/blob/main/advisories/MCSAID-2025-003-scrcpy-global-buffer-overflow.md
