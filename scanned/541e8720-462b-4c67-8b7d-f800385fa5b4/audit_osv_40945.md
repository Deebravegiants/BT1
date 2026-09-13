# [M] Capgo - Arbitrary R2 Object Deletion via Mutable r2_path in app_versions

## Summary
Severity: Medium
Advisory: CVE-2026-56250
Aliases: GHSA-pw8p-5jg6-cxj3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56250
Type: osv

## Details
Capgo before 12.128.2 allows upload-scoped API keys to modify the mutable app_versions.r2_path field through PostgREST, enabling retargeting to arbitrary R2 bundle objects. Attackers can patch r2_path to point to victim objects, soft-delete the attacker-controlled version, and trigger the on_version_update cleanup function to delete the victim R2 object, causing denial of service and bundle availability disruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56250.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-pw8p-5jg6-cxj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-56250
- https://www.vulncheck.com/advisories/capgo-arbitrary-r2-object-deletion-via-mutable-r2-path-in-app-versions
