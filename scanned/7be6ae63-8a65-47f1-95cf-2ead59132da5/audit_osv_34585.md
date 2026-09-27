# [H] Apache Mynewt NimBLE: Incorrect handling of SMP Security Request could lead to undesirable pairing

## Summary
Severity: High
Advisory: CVE-2025-62235
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2025-62235
Type: osv

## Details
Authentication Bypass by Spoofing vulnerability in Apache NimBLE.

Receiving specially crafted Security Request could lead to removal of original bond and re-bond with impostor.
This issue affects Apache NimBLE: through 1.8.0.

Users are recommended to upgrade to version 1.9.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/01/08/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62235.json
- https://lists.apache.org/thread/rw2mrpfwb9d9wmq4h4b6ctcd6gpkk2ho
- https://nvd.nist.gov/vuln/detail/CVE-2025-62235
- https://github.com/apache/mynewt-nimble/commit/41f67e391e788c5feef9030026cc5cbc5431838a
