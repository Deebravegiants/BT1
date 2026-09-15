# [C] CVE-2026-67873

## Summary
Severity: Critical
Advisory: CVE-2026-67873
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-67873
Type: osv

## Details
A heap-based buffer overflow exists in lib60870-C 2.4.0 in the server-side FileSegment ASDU encoding path. The issue occurs because FileSegment_encode() validates only the standalone segment length via FileSegment_GetMaxDataSize() and does not verify the residual capacity of the current ASDU frame before encoding object fields and segment data

## References
- https://github.com/mz-automation/lib60870/blob/master/user_guide.adoc
- https://github.com/mz-automation/lib60870/releases/tag/v2.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67873.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67873
- https://github.com/mz-automation/lib60870/issues/201
- https://github.com/mz-automation/lib60870
