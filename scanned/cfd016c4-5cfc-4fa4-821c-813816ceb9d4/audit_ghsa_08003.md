# [C] FUXA Unauthenticated Remote Arbitrary Device Tag Write

## Summary
Severity: Critical
Advisory: GHSA-ggxw-g3cp-mgf8
CVE: CVE-2026-25752
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:H/SC:L/SI:H/SA:H (CVSS_V4)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-ggxw-g3cp-mgf8
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0 <1.2.10

## Details
### Summary
**Description**
An authorization bypass vulnerability in FUXA allows an unauthenticated, remote attacker to modify device tags via WebSockets. This affects FUXA through version 1.2.9. This issue has been patched in FUXA version 1.2.10.

### Impact
This affects all deployments, including those with `runtime.settings.secureEnabled` set to `true`.

Exploitation allows an unauthenticated, remote attacker to bypass role-based access controls and overwrite arbitrary device tags or disable communication drivers, exposing connected ICS/SCADA environments to follow-on actions. This may allow an attacker to manipulate physical processes and disconnected devices from the HMI.

### Patches
This issue has been patched in FUXA version 1.2.10. Users are strongly encouraged to update to the latest available release.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-ggxw-g3cp-mgf8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25752
- https://github.com/frangoteam/FUXA/commit/eb2d8a20964ce7acaa0f442a181390a5f726a1ae
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.2.10
