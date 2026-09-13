# [M] Ash.Type.UUIDv7 accepts non-v7 UUIDs that then fail to load, causing persistent denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-82738
Aliases: EEF-CVE-2026-82738, GHSA-7xfw-9jwm-9c4c
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82738
Type: osv

## Details
Improper Input Validation vulnerability in ash-project ash allows an attacker to persistently deny reads of a record by storing a non-version-7 UUID in an Ash.Type.UUIDv7 attribute.

Ash.Type.UUIDv7.cast_input/2 accepts any well-formed UUID string, including non-version-7 UUIDs, and stores it as a 16-byte binary. On read, cast_stored/2 (lib/ash/type/uuid_v7.ex) routes the stored binary back through cast_input/2, which since an input-validation tightening in v3.6.3 matches only version-7 (and optionally version-4) 16-byte binaries and otherwise expects a 36-character string. A stored non-v7 16-byte binary matches neither clause and returns :error, so every later read of that record fails. An attacker able to set such an attribute poisons the row permanently. The fix decodes any 16-byte stored binary directly in cast_stored/2.

This issue affects ash: from 3.6.3 before 3.32.2.

## References
- https://cna.erlef.org/cves/CVE-2026-82738.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82738
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82738.json
- https://github.com/ash-project/ash/security/advisories/GHSA-7xfw-9jwm-9c4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-82738
- https://github.com/ash-project/ash/commit/c453cdc0b8570e86ffef0d10e136247f52b3ea76
- https://github.com/ash-project/ash
