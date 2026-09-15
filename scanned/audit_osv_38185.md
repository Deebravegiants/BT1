# [H] openFPGALoader has a heap buffer overflow in BitParser::parseHeader() via crafted .bit file

## Summary
Severity: High
Advisory: CVE-2026-35170
Aliases: GHSA-v59x-fvpj-j22x
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35170
Type: osv

## Details
openFPGALoader is a utility for programming FPGAs. In 1.1.1 and earlier, a heap-buffer-overflow read vulnerability exists in BitParser::parseHeader() that allows out-of-bounds heap memory access when parsing a crafted .bit file. No FPGA hardware is required to trigger this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35170.json
- https://github.com/trabucayre/openFPGALoader/security/advisories/GHSA-v59x-fvpj-j22x
- https://nvd.nist.gov/vuln/detail/CVE-2026-35170
