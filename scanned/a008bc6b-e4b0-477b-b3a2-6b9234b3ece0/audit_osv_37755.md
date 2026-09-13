# [M] GPAC MP4Box Heap Buffer Overflow Write in gf_xml_parse_bit_sequence_bs (NHML BS Parsing)

## Summary
Severity: Medium
Advisory: CVE-2026-33144
Aliases: GHSA-3jw5-9pmw-vmfg
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33144
Type: osv

## Details
GPAC is an open-source multimedia framework. Prior to commit 86b0e36, a heap-based buffer overflow (write) vulnerability was discovered in GPAC MP4Box. The vulnerability exists in the gf_xml_parse_bit_sequence_bs function in utils/xml_bin_custom.c when processing a crafted NHML file containing malicious <BS> (BitSequence) elements. An attacker can exploit this by providing a specially crafted NHML file, causing an out-of-bounds write on the heap. This issue has been via commit 86b0e36.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33144.json
- https://github.com/gpac/gpac/security/advisories/GHSA-3jw5-9pmw-vmfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33144
- https://github.com/gpac/gpac/commit/86b0e36ea4c71402fbdaf7e13d73ba8841003e72
