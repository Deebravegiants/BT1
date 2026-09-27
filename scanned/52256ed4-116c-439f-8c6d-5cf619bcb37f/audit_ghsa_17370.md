# [C] Robocode has an insecure temporary file creation vulnerability in the AutoExtract component

## Summary
Severity: Critical
Advisory: GHSA-2mxr-rc97-xrj2
CVE: CVE-2025-14307
CWE: CWE-377
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/AU:Y/R:U/V:D/RE:M/U:Red (CVSS_V4)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-2mxr-rc97-xrj2
Type: github-advisory

## Affected
- Maven: `net.sf.robocode:robocode.battle` — affected >=0 <1.9.5.6

## Details
An insecure temporary file creation vulnerability exists in the AutoExtract component of Robocode version 1.9.3.6. The createTempFile method fails to securely create temporary files, allowing attackers to exploit race conditions and potentially execute arbitrary code or overwrite critical files. This vulnerability can be exploited by manipulating the temporary file creation process, leading to potential unauthorized actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14307
- https://github.com/robo-code/robocode/pull/68
- https://github.com/robo-code/robocode/commit/9f882bba2a9cd91da57c16b98699f8cc9b354f3a
- https://github.com/robo-code/robocode
