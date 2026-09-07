# [C] Spinnaker clouddriver and orca URL validation bypass via underscores in hostnames

## Summary
Severity: Critical
Advisory: GHSA-8r8j-gfhg-fw38
CVE: CVE-2026-25534
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-8r8j-gfhg-fw38
Type: github-advisory

## Affected
- Maven: `io.spinnaker.clouddriver:clouddriver-artifacts` — affected >=2025.1.6 <2025.2.4
- Maven: `io.spinnaker.clouddriver:clouddriver-artifacts` — affected >=2025.3.0 <2025.3.1
- Maven: `io.spinnaker.clouddriver:clouddriver-artifacts` — affected >=2025.4.0 <2025.4.1
- Maven: `io.spinnaker.orca:orca-core` — affected >=2025.1.6 <2025.2.4
- Maven: `io.spinnaker.orca:orca-core` — affected >=2025.3.0 <2025.3.1
- Maven: `io.spinnaker.orca:orca-core` — affected >=2025.4.0 <2025.4.1

## Details
### Impact
Spinnaker updated URL Validation logic on user input to provide sanitation on user inputted URLs for clouddriver.  However, they missed that Java URL objects do not correctly handle underscores on parsing.  This led to a bypass of the previous CVE (CVE-2025-61916) through the use of carefully crafted URLs.  Note, Spinnaker found this not just in that CVE, but in the existing URL validations in Orca fromUrl expression handling.  This CVE impacts BOTH artifacts as a result.   

### Patches
This has been merged and will be available in versions 2025.4.1, 2025.3.1, 2025.2.4 and 2026.0.0.  

### Workarounds
You can disable the various artifacts on this system to work around these limits.

## References
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-8r8j-gfhg-fw38
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-vrjc-q2fh-6x9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25534
- https://github.com/spinnaker/spinnaker/commit/7c4737906239a958a468e843239c6785b03d0eda
- https://github.com/spinnaker/spinnaker
