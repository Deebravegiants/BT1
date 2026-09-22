# [C] Code injection in Duke

## Summary
Severity: Critical
Advisory: GHSA-p83q-99rc-vfmv
CVE: CVE-2023-39013
CWE: CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-p83q-99rc-vfmv
Type: github-advisory

## Affected
- Maven: `no.priv.garshol.duke:duke` — affected >=0

## Details
Duke v1.2 and below was discovered to contain a code injection vulnerability via the component no.priv.garshol.duke.server.CommonJTimer.init.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39013
- https://github.com/larsga/Duke/issues/273
- https://github.com/larsga/Duke
