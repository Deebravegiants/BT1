# [H] jackson-databind possible Denial of Service if using JDK serialization to serialize JsonNode

## Summary
Severity: High
Advisory: GHSA-3x8x-79m2-3w2w
CVE: CVE-2021-46877
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-19
Source: https://github.com/advisories/GHSA-3x8x-79m2-3w2w
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.10.0 <2.12.6
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.13.0 <2.13.1

## Details
jackson-databind 2.10.x through 2.12.x before 2.12.6 and 2.13.x before 2.13.1 allows attackers to cause a denial of service (2 GB transient heap usage per read) in uncommon situations involving JsonNode JDK serialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46877
- https://github.com/FasterXML/jackson-databind/issues/3328
- https://github.com/FasterXML/jackson-databind/commit/3ccde7d938fea547e598fdefe9a82cff37fed5cb
- https://github.com/FasterXML/jackson-databind
- https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.12.6
- https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.13.1
- https://groups.google.com/g/jackson-user/c/OsBsirPM_Vw
