# [H] Caucho Quercus, as distributed in Resin, does not properly handle unspecified characters in the names of variables

## Summary
Severity: High
Advisory: GHSA-p332-fw36-4hqx
CVE: CVE-2012-2965
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p332-fw36-4hqx
Type: github-advisory

## Affected
- Maven: `com.caucho:resin` — affected >=0 <4.0.29

## Details
Caucho Quercus, as distributed in Resin before 4.0.29, does not properly handle unspecified characters in the names of variables, which has unknown impact and remote attack vectors, related to an "HTTP Parameter Contamination" issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2965
- https://web.archive.org/web/20131210160901/http://en.securitylab.ru:80/lab/PT-2012-05
- http://caucho.com/resin-4.0/changes/changes.xtp
- http://en.securitylab.ru/lab
- http://www.kb.cert.org/vuls/id/309979
