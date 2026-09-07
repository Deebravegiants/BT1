# [H] Data Amplification in Play Framework

## Summary
Severity: High
Advisory: GHSA-r8rm-4hfj-2x87
CVE: CVE-2020-26882
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-r8rm-4hfj-2x87
Type: github-advisory

## Affected
- Maven: `com.typesafe.play:play` — affected >=2.6.0 <2.7.6
- Maven: `com.typesafe.play:play` — affected >=2.8.0 <2.8.3

## Details
In Play Framework 2.6.0 through 2.8.2, data amplification can occur when an application accepts multipart/form-data JSON input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26882
- https://github.com/playframework/playframework/pull/10495
- https://www.playframework.com/security/vulnerability/CVE-2020-26882-JsonParseDataAmplification
