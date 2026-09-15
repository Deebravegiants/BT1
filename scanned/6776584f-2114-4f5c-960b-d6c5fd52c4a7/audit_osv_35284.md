# [M] CVE-2025-70309

## Summary
Severity: Medium
Advisory: CVE-2025-70309
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2025-70309
Type: osv

## Details
A stack overflow in the pcmreframe_flush_packet function of GPAC v2.4.0 allows attackers to cause a Denial of Service (DoS) via a crafted WAV file.

## References
- https://github.com/zakkanijia/POC/blob/main/gpac_rawpcm/GPAC_RFPCM.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70309.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70309
