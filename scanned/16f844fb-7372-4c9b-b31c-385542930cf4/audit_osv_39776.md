# [M] NULL Pointer Dereference in REST API properties_parse via Malformed user_properties

## Summary
Severity: Medium
Advisory: CVE-2026-47276
Aliases: GHSA-qq2v-xvxg-3hvf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-47276
Type: osv

## Details
In nanomq versions 0.24.11 and earlier, a NULL pointer dereference in `properties_parse()` allows an authenticated attacker to crash the NanoMQ broker by sending a POST request to `/api/v4/mqtt/publish` with `user_properties` as a JSON array instead of a JSON object. The crash occurs because `strlen()` is called on a NULL `item->string` pointer when iterating over array elements. An authenticated attacker can exploit this to crash the NanoMQ broker process. This is patched in version 0.24.14.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47276.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-qq2v-xvxg-3hvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-47276
