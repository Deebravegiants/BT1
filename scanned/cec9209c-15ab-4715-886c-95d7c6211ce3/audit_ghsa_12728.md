# [H] ReDoS Vulnerability in ua-parser-js version

## Summary
Severity: High
Advisory: GHSA-fhg7-m89q-25r3
CVE: CVE-2022-25927
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-24
Source: https://github.com/advisories/GHSA-fhg7-m89q-25r3
Type: github-advisory

## Affected
- npm: `ua-parser-js` — affected >=0.7.30 <0.7.33
- npm: `ua-parser-js` — affected >=0.8.0 <1.0.33

## Details
### Description:
A regular expression denial of service (ReDoS) vulnerability has been discovered in `ua-parser-js`.

### Impact:
This vulnerability bypass the library's `MAX_LENGTH` input limit prevention. By crafting a very-very-long user-agent string with specific pattern, an attacker can turn the script to get stuck processing for a very long time which results in a denial of service (DoS) condition.

### Affected Versions:
From version `0.7.30` to before versions `0.7.33` / `1.0.33`.

### Patches:
A patch has been released to remove the vulnerable regular expression, update to version `0.7.33` / `1.0.33` or later.

### References:
[Regular expression Denial of Service - ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)

### Credits:
Thanks to @Snyk who first reported the issue.

## References
- https://github.com/faisalman/ua-parser-js/security/advisories/GHSA-fhg7-m89q-25r3
- https://nvd.nist.gov/vuln/detail/CVE-2022-25927
- https://github.com/faisalman/ua-parser-js/commit/a6140a17dd0300a35cfc9cff999545f267889411
- https://github.com/faisalman/ua-parser-js
- https://security.snyk.io/vuln/SNYK-JS-UAPARSERJS-3244450
