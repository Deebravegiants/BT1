# [H] Uncontrolled Resource Consumption in spray-json when parsing decimal digit fields

## Summary
Severity: High
Advisory: GHSA-f94m-mqhr-mc29
CVE: CVE-2018-18853
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-f94m-mqhr-mc29
Type: github-advisory

## Affected
- Maven: `io.spray:spray-json_2.12` — affected >=0 <1.3.5
- Maven: `io.spray:spray-json_2.11` — affected >=0 <1.3.5
- Maven: `io.spray:spray-json_2.10` — affected >=0 <1.3.5

## Details
Lightbend Spray spray-json through 1.3.4 allows remote attackers to cause a denial of service (resource consumption) because of Algorithmic Complexity during the parsing of a field composed of many decimal digits.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18853
- https://github.com/spray/spray-json/issues/278
- https://github.com/advisories/GHSA-f94m-mqhr-mc29
- https://github.com/spray/spray-json
