# [M] CVE-2025-70310

## Summary
Severity: Medium
Advisory: CVE-2025-70310
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2025-70310
Type: osv

## Details
A heap overflow in the vorbis_to_intern() function of GPAC v2.4.0 allows attackers to cause a Denial of Service (DoS) via a crafted .ogg file.

## References
- https://github.com/zakkanijia/POC/blob/main/gpac_dec_vorbis/GPAC_VORBIS.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70310.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70310
