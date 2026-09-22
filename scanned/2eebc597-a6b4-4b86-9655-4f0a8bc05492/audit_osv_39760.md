# [M] NanaZip: Heap out-of-bounds read in NanaZip AVB property descriptor parser via unsigned integer underflow

## Summary
Severity: Medium
Advisory: CVE-2026-47222
Aliases: GHSA-mqqj-crf3-6q37
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47222
Type: osv

## Details
NanaZip is the 7-Zip derivative intended for the modern Windows experience. From version 3.0.1000.0 to before version 6.0.1698.0, a heap out-of-bounds read exists in the Android Verified Boot (AVB) vbmeta image parser in NanaZip (via the upstream 7-Zip AvbHandler). An unsigned integer underflow in a bounds check allows an attacker-controlled value_num_bytes field to pass validation, causing AddNameToString to read up to ~4 GiB past the end of a 64 KiB heap buffer. This causes a deterministic crash (denial of service) when opening a crafted .avb or .img file. This issue has been patched in stable version 6.0.1698.0 and preview version 6.5.1742.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47222.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-mqqj-crf3-6q37
- https://nvd.nist.gov/vuln/detail/CVE-2026-47222
