# [M] Cross-Site Scripting in Grav

## Summary
Severity: Medium
Advisory: GHSA-cvmr-6428-87w9
CWE: CWE-79
Ecosystem: Packagist
Published: 2020-12-10
Source: https://github.com/advisories/GHSA-cvmr-6428-87w9
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.6.30

## Details
### Impact
Privileged users (with the ability to edit pages) have a mechanism to perform remote code execution via XSS. At a minimum, the vulnerability represents a bypass of security controls put in place to mitigate this form of attack.

The remote code execution can be performed because XSS would allow an attacker to execute functionality on behalf of a stolen administrative account - the facility to install custom plugins would then allow said attacker to install a plugin containing a web shell and thus garner access to the underlying system.

### References
https://owasp.org/www-project-top-ten/2017/A7_2017-Cross-Site_Scripting_(XSS)
https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
https://cwe.mitre.org/data/definitions/79.html

### For more information
Please contact contact@pentest.co.uk

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-cvmr-6428-87w9
