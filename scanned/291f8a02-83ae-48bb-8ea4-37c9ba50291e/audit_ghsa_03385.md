# [C] Arbitrary code execution in djv

## Summary
Severity: Critical
Advisory: GHSA-4hv7-3q38-97m8
CVE: CVE-2020-28464
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-4hv7-3q38-97m8
Type: github-advisory

## Affected
- npm: `djv` — affected >=0 <2.1.4

## Details
This affects the package djv before 2.1.4. By controlling the schema file, an attacker can run arbitrary JavaScript code on the victim machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28464
- https://github.com/korzio/djv/pull/98/files
- https://github.com/korzio/djv/blob/master/lib/utils/properties.js%23L55
- https://snyk.io/vuln/SNYK-JS-DJV-1014545
