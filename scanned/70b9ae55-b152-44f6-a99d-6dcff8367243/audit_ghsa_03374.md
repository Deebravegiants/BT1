# [H] OS Command Injection in serial-number

## Summary
Severity: High
Advisory: GHSA-3fw4-4h3m-892h
CVE: CVE-2019-10804
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-3fw4-4h3m-892h
Type: github-advisory

## Affected
- npm: `serial-number` — affected >=0

## Details
serial-number through 1.3.0 allows execution of arbritary commands. The &quot;cmdPrefix&quot; argument in serialNumber function is used by the &quot;exec&quot; function without any validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10804
- https://github.com/es128/serial-number/blob/master/index.js#L106
- https://snyk.io/vuln/SNYK-JS-SERIALNUMBER-559010
