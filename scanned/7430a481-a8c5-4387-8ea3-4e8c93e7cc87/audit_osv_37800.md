# [M] OpenEMR has Authorization Bypass in FaxSMS AppDispatch Constructor

## Summary
Severity: Medium
Advisory: CVE-2026-33305
Aliases: GHSA-r973-h5cq-35rc
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-33305
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.2, an authorization bypass in the optional FaxSMS module (`oe-module-faxsms`) allows any authenticated OpenEMR user to invoke controller methods — including `getNotificationLog()`, which returns patient appointment data (PHI) — regardless of whether they hold the required ACL permissions. The `AppDispatch` constructor dispatches user-controlled actions and exits the process before any calling code can enforce ACL checks. Version 8.0.0.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33305.json
- https://github.com/openemr/openemr/security/advisories/GHSA-r973-h5cq-35rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33305
- https://github.com/openemr/openemr/commit/edb65936e259b2625e8eea4628316c4577cb2a11
