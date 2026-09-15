# [M] SumatraPDF's Integer Underflow in PalmDbReader Leads to Crash

## Summary
Severity: Medium
Advisory: CVE-2026-23951
Aliases: GHSA-hj4w-c5x8-p2hv
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-23951
Type: osv

## Details
SumatraPDF is a multi-format reader for Windows. All versions contain an off-by-one error in the validation code that only triggers with exactly 2 records, causing an integer underflow in the size calculation. This bug exists in PalmDbReader::GetRecord when opening a crafted Mobi file, resulting in an out-of-bounds heap read that crashes the app. There are no published fixes at the time of publication.

## References
- https://github.com/sumatrapdfreader/sumatrapdf/blob/master/src/PalmDbReader.cpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23951.json
- https://github.com/sumatrapdfreader/sumatrapdf/security/advisories/GHSA-hj4w-c5x8-p2hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-23951
