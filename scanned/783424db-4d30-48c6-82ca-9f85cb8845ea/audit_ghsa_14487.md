# [H] Jettison vulnerable to infinite recursion

## Summary
Severity: High
Advisory: GHSA-q6g2-g7f3-rr83
CVE: CVE-2023-1436
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-22
Source: https://github.com/advisories/GHSA-q6g2-g7f3-rr83
Type: github-advisory

## Affected
- Maven: `org.codehaus.jettison:jettison` — affected >=0 <1.5.4

## Details
An infinite recursion is triggered in Jettison when constructing a JSONArray from a Collection that contains a self-reference in one of its elements. This leads to a StackOverflowError exception being thrown.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1436
- https://github.com/jettison-json/jettison/issues/60
- https://github.com/jettison-json/jettison/pull/62
- https://github.com/jettison-json/jettison
- https://github.com/jettison-json/jettison/releases/tag/jettison-1.5.4
- https://research.jfrog.com/vulnerabilities/jettison-json-array-dos-xray-427911
