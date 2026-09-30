# [C] FUXA Unauthenticated Remote Code Execution via Hardcoded JWT Secret in Default Configuration

## Summary
Severity: Critical
Advisory: GHSA-32cc-x95p-fxcg
CVE: CVE-2026-25894
CWE: CWE-1188, CWE-321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-32cc-x95p-fxcg
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0 <1.2.10

## Details
### Description
An insecure default configuration in FUXA allows an unauthenticated, remote attacker to gain administrative access and execute arbitrary code on the server. This affects FUXA through version 1.2.9 when authentication is enabled, but the administrator JWT secret is not configured. This issue has been patched in FUXA version 1.2.10.

### Impact
The FUXA documentation allows administrators to manually update a hardcoded JWT secret when enabling authentication. This feature was not available in the UI. This results in a fail-open security posture, where the application can report or appear to be operating in `secureEnabled` mode while still accepting tokens signed with a publicly known key.

Exploitation allows an unauthenticated, remote attacker to forge JWTs to bypass all authentication mechanisms and obtain administrative access to the FUXA instance. With these elevated privileges, the attacker can interact with administrative APIs, including intended features designed for automation and scripting, to execute arbitrary code in the context of the FUXA service. Depending on deployment configuration and permissions, this may lead to full system compromise and could further expose connected ICS/SCADA environments to follow-on actions.

### Patches
This issue has been patched in FUXA version 1.2.10. Users are strongly encouraged to update to the latest available release.

### Notes
GitHub stated this vulnerability is identical to CVE-2025-69971, which was published against the repository out of band before coordinated disclosure concluded. CVE-2025-69971 is directionally correct, but the description is inaccurate. Please refer to this advisory for the proper description and affected versions.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-32cc-x95p-fxcg
- https://nvd.nist.gov/vuln/detail/CVE-2026-25894
- https://github.com/frangoteam/FUXA/commit/ea7b3df066f9fdef8ecdce318398ae40546bc50d
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.2.10
