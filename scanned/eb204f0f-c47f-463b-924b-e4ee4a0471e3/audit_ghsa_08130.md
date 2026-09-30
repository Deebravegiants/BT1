# [C] FUXA Unauthenticated Remote Arbitrary Scheduler Write

## Summary
Severity: Critical
Advisory: GHSA-c869-jx4c-q5fc
CVE: CVE-2026-25939
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H (CVSS_V4)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-c869-jx4c-q5fc
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=1.2.8 <1.2.11

## Details
### Summary
An authorization bypass vulnerability in the FUXA allows an unauthenticated, remote attacker to create and modify arbitrary schedulers, exposing connected ICS/SCADA environments to follow-on actions. This vulnerability affects FUXA version 1.2.8 through version 1.2.10. This has been patched in FUXA version 1.2.11.

### Impact
This affects all deployments, including those with `runtime.settings.secureEnabled` set to `true`.

Exploitation allows an unauthenticated, remote attacker to automatically authenticate as guest and create, modify or delete schedules. These schedules can be configured to trigger immediately or cyclically, forcing connected devices to specific states or values, or executing existing scripts on the server.

### Patches

This issue has been patched in FUXA version 1.2.11. Users are strongly encouraged to update to the latest available release.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-c869-jx4c-q5fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-25939
- https://github.com/frangoteam/FUXA/pull/2174
- https://github.com/frangoteam/FUXA/commit/5782b35117a9bd14ffcb881f8dfb8c6680157d9b
- https://github.com/frangoteam/FUXA/commit/aced6ad0b6089eea4e5cef51c0a88bf4f308d45f
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.2.11
