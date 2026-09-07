# [C] FUXA Unauthenticated Remote Code Execution in Node-RED Integration

## Summary
Severity: Critical
Advisory: GHSA-v4p5-w6r3-2x4f
CVE: CVE-2026-25938
CWE: CWE-290, CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-v4p5-w6r3-2x4f
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=1.2.8 <1.2.11

## Details
### Summary

**Description**
An authentication bypass vulnerability in FUXA allows an unauthenticated, remote attacker to execute arbitrary code on the server when the Node-RED plugin is enabled. This affects FUXA version 1.2.8 through version 1.2.10. This has been patched in FUXA version 1.2.11.

### Impact
This affects all deployments with the Node-RED plugin enabled, including those with `runtime.settings.secureEnabled` set to true.

Exploitation allows an unauthenticated, remote attacker to send a specially crafted request to the `/nodered/flows` endpoint to bypass authentication checks, granting the attacker administrative access to the Node-RED deployment API. By submitting a malicious flow configuration, an attacker can execute arbitrary code in the context of the FUXA service. Depending on deployment configuration and permissions, this may lead to full system compromise and could further expose connected ICS/SCADA environments to follow-on actions.

### Patches
This issue has been patched in FUXA version 1.2.11. Users are strongly encouraged to update to the latest available release.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-v4p5-w6r3-2x4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25938
- https://github.com/frangoteam/FUXA/commit/5e7679b09718534e4501a146fdfe093da29af336
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.2.11
