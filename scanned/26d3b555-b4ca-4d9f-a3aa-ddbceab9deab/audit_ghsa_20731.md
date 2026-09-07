# [H] Polynomial regular expression used on uncontrolled data in nitrado.js

## Summary
Severity: High
Advisory: GHSA-vqc4-v8hc-h2jg
CVE: CVE-2022-36034
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-31
Source: https://github.com/advisories/GHSA-vqc4-v8hc-h2jg
Type: github-advisory

## Affected
- npm: `nitrado.js` — affected >=0 <0.2.5

## Details
### Impact
Possible ReDoS with lib input of `{{` and with many repetitions of `{{|`

### Patches
Patched in all versions above `0.2.5`

### Workarounds
No known work arounds.

### References
- OWASP: [Regular expression Denial of Service - ReDoS](https://www.owasp.org/index.php/Regular_expression_Denial_of_Service_-_ReDoS)
- Wikipedia: [ReDoS](https://en.wikipedia.org/wiki/ReDoS).
- Wikipedia: [Time complexity](https://en.wikipedia.org/wiki/Time_complexity).
- James Kirrage, Asiri Rathnayake, Hayo Thielecke: [Static Analysis for Regular Expression Denial-of-Service Attack](http://www.cs.bham.ac.uk/~hxt/research/reg-exp-sec.pdf).
- Common Weakness Enumeration: [CWE-1333](https://cwe.mitre.org/data/definitions/1333.html).
- Common Weakness Enumeration: [CWE-400](https://cwe.mitre.org/data/definitions/400.html).

## References
- https://github.com/cainthebest/nitrado.js/security/advisories/GHSA-vqc4-v8hc-h2jg
- https://nvd.nist.gov/vuln/detail/CVE-2022-36034
- https://github.com/cainthebest/nitrado.js
- https://github.com/cainthebest/nitrado.js/blob/v0.2.5/CHANGELOG.md
