# [C] FUXA Unauthenticated Remote Code Execution via Admin JWT Minting

## Summary
Severity: Critical
Advisory: GHSA-vwcg-c828-9822
CVE: CVE-2026-25893
CWE: CWE-285, CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-vwcg-c828-9822
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0 <1.2.10

## Details
### Note
GitHub incorrectly stated this vulnerability is identical to CVE-2025-69970, which describes the fact that authentication is disabled by default. This advisory describes an exploit chain that enables authentication bypass via the heartbeat refresh endpoint when authentication is enabled. This misleads users into thinking that enabling authentication would mitigate this vulnerability. Please see the patch for more information: https://github.com/frangoteam/FUXA/commit/fe82348d160904d0013b9a3e267d50158f5c7afb.

### Description
An authentication bypass vulnerability in FUXA allows an unauthenticated, remote attacker to gain administrative access via the heartbeat refresh API and execute arbitrary code on the server. This affects FUXA through version 1.2.9 when authentication is enabled. This issue has been patched in FUXA version 1.2.10.

### Impact
Affected deployments are those with `runtime.settings.secureEnabled` set to `true`.

Exploitation allows an unauthenticated, remote attacker to bypass all authentication mechanisms and obtain administrative access to the FUXA instance by minting administrator JWTs via the heartbeat refresh endpoint. With these elevated privileges, the attacker can interact with administrative APIs, including intended features designed for automation and scripting, to execute arbitrary code in the context of the FUXA service. Depending on deployment configuration and permissions, this may lead to full system compromise and could further expose connected ICS/SCADA environments to follow-on actions.

### Patches
This issue has been patched in FUXA version 1.2.10. Users are strongly encouraged to update to the latest available release.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-vwcg-c828-9822
- https://nvd.nist.gov/vuln/detail/CVE-2026-25893
- https://github.com/frangoteam/FUXA/commit/fe82348d160904d0013b9a3e267d50158f5c7afb
- https://github.com/frangoteam/FUXA
