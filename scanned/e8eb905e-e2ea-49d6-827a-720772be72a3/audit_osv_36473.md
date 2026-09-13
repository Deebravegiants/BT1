# [H] Golioth Pouch (prior to commit 1b2219a1) BLE GATT Heap-based Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-23750
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-23750
Type: osv

## Details
Golioth Pouch version 0.1.0, prior to commit 1b2219a1, contains a heap-based buffer overflow in BLE GATT server certificate handling. server_cert_write() allocates a heap buffer of size CONFIG_POUCH_SERVER_CERT_MAX_LEN when receiving the first fragment, then appends subsequent fragments using memcpy() without verifying that sufficient capacity remains. An adjacent BLE client can send unauthenticated fragments whose combined size exceeds the allocated buffer, causing a heap overflow and crash; integrity impact is also possible due to memory corruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23750.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23750
- https://www.vulncheck.com/advisories/golioth-pouch-ble-gatt-heap-based-buffer-overflow
- https://github.com/golioth/pouch/commit/1b2219a1
- https://github.com/golioth/pouch
- https://secmate.dev/disclosures/SECMATE-2025-0018
- https://blog.secmate.dev/posts/golioth-vulnerabilities-disclosure/
