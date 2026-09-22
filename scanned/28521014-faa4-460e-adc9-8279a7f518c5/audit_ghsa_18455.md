# [C] LaRecipe is vulnerable to Server-Side Template Injection attacks

## Summary
Severity: Critical
Advisory: GHSA-jv7x-xhv2-p5v2
CVE: CVE-2025-53833
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-14
Source: https://github.com/advisories/GHSA-jv7x-xhv2-p5v2
Type: github-advisory

## Affected
- Packagist: `binarytorch/larecipe` — affected >=0 <2.8.1

## Details
### Impact
Attackers could:
1. Execute arbitrary commands on the server
2. Access sensitive environment variables
3. Escalate access depending on server configuration

A critical vulnerability was discovered in LaRecipe that allows an attacker to perform Server-Side Template Injection (SSTI), potentially leading to Remote Code Execution (RCE) in vulnerable configurations.

### Patches
Users are strongly advised to upgrade to version v2.8.1 or later.

### Credit
We would like to thank **Roman Ananev** for responsibly identifying and reporting this vulnerability.

## References
- https://github.com/saleem-hadad/larecipe/security/advisories/GHSA-jv7x-xhv2-p5v2
- https://nvd.nist.gov/vuln/detail/CVE-2025-53833
- https://github.com/saleem-hadad/larecipe/pull/390
- https://github.com/saleem-hadad/larecipe/commit/c1d0d56889655ce5f2645db5acf0e78d5fc3b36b
- https://github.com/saleem-hadad/larecipe
