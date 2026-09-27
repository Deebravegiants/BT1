# [M] OpenEMR Missing ACL Checks on Insurance Company API Routes

## Summary
Severity: Medium
Advisory: CVE-2026-33915
Aliases: GHSA-ww94-26v7-x4gp
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33915
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, five insurance company REST API routes are missing the `RestConfig::request_authorization_check()` call that every other data-modifying route in the standard API uses. This allows any authenticated API user to create and modify insurance company records even if their OpenEMR user account does not have administrative ACL permissions. Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33915.json
- https://github.com/openemr/openemr/security/advisories/GHSA-ww94-26v7-x4gp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33915
- https://github.com/openemr/openemr/commit/976d2a85f024a730955578597a82c083067a72b4
