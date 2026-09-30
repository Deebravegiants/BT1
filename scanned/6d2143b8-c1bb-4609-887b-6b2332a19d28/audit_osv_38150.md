# [M] barebox ext4 Extent Parsing Out-of-Bounds Read

## Summary
Severity: Medium
Advisory: CVE-2026-34961
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-34961
Type: osv

## Details
barebox prior to version 2026.04.0 contains out-of-bounds read vulnerabilities in ext4 extent parsing due to missing validation of the eh_entries field against buffer capacity in fs/ext4/ext4_common.c. Attackers can supply a malicious ext4 filesystem image via USB, SD card, or network boot to trigger heap out-of-bounds reads during boot-time filesystem parsing, potentially redirecting reads to arbitrary disk offsets.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34961.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34961
- https://www.vulncheck.com/advisories/barebox-ext4-extent-parsing-out-of-bounds-read
- https://github.com/barebox/barebox/releases/tag/v2026.04.0
- https://github.com/barebox/barebox
- https://y637f9qq2x.com/posts/barebox-sandbox-vulns/
