# [C] FUXA Unauthenticated Remote Code Execution via Arbitrary File Write in Upload API

## Summary
Severity: Critical
Advisory: GHSA-88qh-cphv-996c
CVE: CVE-2026-25895
CWE: CWE-22, CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-88qh-cphv-996c
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0 <1.2.10

## Details
### Summary
**Description**
A path traversal vulnerability in FUXA allows an unauthenticated, remote attacker to write arbitrary files to arbitrary locations on the server filesystem. This affects FUXA through version 1.2.9. This issue has been patched in FUXA version 1.2.10.

### Impact
This affects all deployments, including those with `runtime.settings.secureEnabled` set to `true`.

Exploitation allows an unauthenticated, remote attacker to overwrite application and system files. If the attacker can overwrite application code, startup scripts, or configuration files that are later executed/loaded, RCE is likely. Depending on deployment configuration and permissions, this may lead to full system compromise and could further expose connected ICS/SCADA environments to follow-on actions.

### Patches
This issue has been patched in FUXA version 1.2.10. Users are strongly encouraged to update to the latest available release.

### Notes
GitHub stated this vulnerability is identical to CVE-2025-69981, which was published against the repository out of band before coordinated disclosure concluded. CVE-2025-69981 describes a "CWE-434: Unrestricted Upload of File with Dangerous Type" vulnerability. While a CWE-434 is present, it was an unsafe, intended feature of the application that has been locked behind authentication. This report describes a "CWE-35: Path Traversal" that enables an arbitrary file write.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-88qh-cphv-996c
- https://nvd.nist.gov/vuln/detail/CVE-2026-25895
- https://github.com/frangoteam/FUXA/commit/22c2192f5d9beef8a787c45eff3a14c24dbb5f96
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.2.10
