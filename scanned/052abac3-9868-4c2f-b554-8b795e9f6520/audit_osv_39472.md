# [H] Apache NimBLE: Remote reachable assertion in ATT Read Multiple Variable Response handler

## Summary
Severity: High
Advisory: CVE-2026-45815
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-45815
Type: osv

## Details
Reachable Assertion vulnerability in Apache NimBLE.
A specially crafted ATT Read Multiple Variable Response (BLE_ATT_OP_READ_MULT_VAR_RSP) may trigger assert in ATT parser.

Severity is medium as this requires DUT to first send ATT Read Multiple Variable Request.

This issue affects Apache NimBLE: through 1.9.0.

Users are recommended to upgrade to version 1.10.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45815.json
- https://lists.apache.org/thread/3d09hgo5zmm7dnryst3tb9857hk1bbos
- https://nvd.nist.gov/vuln/detail/CVE-2026-45815
- https://github.com/apache/mynewt-nimble/commit/fae6a4874309ba0175d2c444e20f8a6bde007425
