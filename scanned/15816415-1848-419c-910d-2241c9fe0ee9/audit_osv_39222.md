# [M] Stack buffer overflows in SimpleBLE

## Summary
Severity: Medium
Advisory: CVE-2026-44634
Aliases: GHSA-8h89-q8m2-c8fp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-44634
Type: osv

## Details
SimpleBLE is a cross-platform library and bindings for Bluetooth Low Energy (BLE). Prior to version 0.14.0, there are multiple stack-based buffer overflow vulnerabilities in SimpleBLE. There is a stack overflow vulnerability in the dongl backend’s Protocol::simpleble_write function (local, caller-controlled input). A stack overflow vulnerability when processing manufacturer-specific data in BLE advertisements (remote, no pairing or connection required). Lastly, a stack overflow vulnerability when processing service data in BLE advertisements (remote, no pairing or connection required). This issue has been patched in version 0.14.0.

## References
- https://github.com/simpleble/simpleble/releases/tag/v0.14.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44634.json
- https://github.com/simpleble/simpleble/security/advisories/GHSA-8h89-q8m2-c8fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-44634
- https://github.com/simpleble/simpleble/commit/1501d59d76a4280268372afb1b157bf6caeacba6
- https://github.com/simpleble/simpleble/pull/466
