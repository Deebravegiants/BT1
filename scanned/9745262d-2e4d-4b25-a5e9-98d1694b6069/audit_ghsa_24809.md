# [H] Opencast RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-qwfv-5jwj-582h
CVE: CVE-2017-1000217
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qwfv-5jwj-582h
Type: github-advisory

## Affected
- Maven: `org.opencastproject:base` — affected >=0 <2.3.3

## Details
Opencast 2.3.2 and older versions are vulnerable to script injections through media and metadata in the player and media module resulting in arbitrary code execution, fixed in 2.3.3 and 3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000217
- https://github.com/opencast/opencast/commit/2d42e42f3cfcff3a775a2538f735fca8542ce1fc
- https://github.com/opencast/opencast/commit/fba2f35df24ce2aeaff627200065cbade9b3a0cd
- https://github.com/opencast/opencast
- https://groups.google.com/a/opencast.org/forum/#!topic/security-notices/sCpt0pIPEFg
