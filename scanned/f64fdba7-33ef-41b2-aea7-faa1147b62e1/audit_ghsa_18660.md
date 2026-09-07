# [C] Melis Platform CMS Unauthenticated Admin Account Creation

## Summary
Severity: Critical
Advisory: GHSA-p3vc-g9f9-mgw4
CVE: CVE-2025-10352
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-p3vc-g9f9-mgw4
Type: github-advisory

## Affected
- Packagist: `melisplatform/melis-core` — affected >=0 <5.3.11

## Details
Vulnerability in the melis-core module of Melis Technology's Melis Platform, which, if exploited, allows an unauthenticated attacker to create an administrator account via a request to '/melis/MelisCore/ToolUser/addNewUser'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10352
- https://github.com/melisplatform/melis-core/commit/e938dd14e108b921e6a399b35976dfb429c41df5
- https://github.com/ivansmc00/CVE-2025-10352-POC
- https://github.com/melisplatform/melis-core
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-melis-platform
