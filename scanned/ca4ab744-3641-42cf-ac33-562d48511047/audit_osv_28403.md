# [M] Tolgee' API keys created by server admin users bypass the permission check

## Summary
Severity: Medium
Advisory: CVE-2024-32470
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-18
Source: https://osv.dev/vulnerability/CVE-2024-32470
Type: osv

## Details
Tolgee is an open-source localization platform. When API key created by admin user is used it bypasses the permission check at all. This error was introduced in v3.57.2 and immediately fixed in v3.57.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32470.json
- https://github.com/tolgee/tolgee-platform/security/advisories/GHSA-pm57-hcm8-38gw
- https://github.com/tolgee/tolgee-platform/security/advisories/GHSA-r95p-fqqv-fppc
- https://nvd.nist.gov/vuln/detail/CVE-2024-32470
- https://github.com/tolgee/tolgee-platform/commit/a0d861028d931f8a54387770eaf3a75031b81234
