# [H] FUXA Affected by a Path Traversal Sanitization Bypass

## Summary
Severity: High
Advisory: GHSA-68m5-5w2h-h837
CVE: CVE-2026-25951
CWE: CWE-184, CWE-22, CWE-23
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-68m5-5w2h-h837
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0 <1.2.11

## Details
### Summary
A flaw in the path sanitization logic allows an authenticated attacker with administrative privileges to bypass directory traversal protections. By using nested traversal sequences (e.g., ....//), an attacker can write arbitrary files to the server filesystem, including sensitive directories like runtime/scripts. This leads to Remote Code Execution (RCE) when the server reloads the malicious scripts. It is a new vulnerability a patch bypass for the sanitization in the last release .


### Details
This report describes a new, distinct vulnerability that differs from previous Path Traversal advisories (such as CVE-2023-31718) in several ways:

Patch Bypass (Regression): The vulnerability circumvents the existing sanitization logic implemented to fix previous traversal issues. The current "single-pass" regex approach is insufficient against nested sequences.
Expansion of Scope: Unlike previous reports that focused primarily on /api/download, this bypass affects multiple critical endpoints, including /api/upload, /api/resources/remove, and /api/logs.
Escalation to RCE: By targeting the 
upload
 and remove functionalities, this vulnerability directly leads to Remote Code Execution, which is a higher impact than the information disclosure typically associated with previous traversal reports.


### Impact
Remote Code Execution (RCE): Transition from application admin to full system control.
SCADA Operational Disruption: Potential for physical or operational sabotage by manipulating tags and alarms.
Data Integrity & Availability: Full access to projects, credentials, and historical logs.

### Patches

This issue has been patched in FUXA version 1.2.11. Users are strongly encouraged to update to the latest available release.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-68m5-5w2h-h837
- https://nvd.nist.gov/vuln/detail/CVE-2026-25951
- https://github.com/frangoteam/FUXA/pull/2177
- https://github.com/frangoteam/FUXA/commit/3ecce46333ed33e3f66f378e38e317cde702b0ae
- https://github.com/frangoteam/FUXA/commit/f7a9f04b2ab97ab5421e4ec4e711c51e9f4b65c8
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.2.11
