# [H] Server-Side Template Injection

## Summary
Severity: High
Advisory: GHSA-wmfg-55f9-j8hq
CVE: CVE-2020-26282
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-12-24
Source: https://github.com/advisories/GHSA-wmfg-55f9-j8hq
Type: github-advisory

## Affected
- Maven: `com.browserup:browserup-proxy` — affected >=0 <2.1.2

## Details
### Impact
A Server-Side Template Injection was identified in BrowserUp Proxy enabling attackers to inject arbitrary Java EL expressions, leading to unauthenticated Remote Code Execution (RCE) vulnerability. This has been assigned CVE-2020-26282.

### Patches
Effective Immediately, all users should upgrade to version 2.1.2 or higher.

### Workarounds
None. 

### References
https://securitylab.github.com/research/bean-validation-RCE


### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the BrowserUp Proxy repo](http://github.com/browserup/browserup-proxy)
* Contact us via  the [BrowserUp website](https://browserup.com) or email us at [support@browserup.com](mailto:support@browserup.com)

## References
- https://github.com/browserup/browserup-proxy/security/advisories/GHSA-wmfg-55f9-j8hq
- https://nvd.nist.gov/vuln/detail/CVE-2020-26282
- https://github.com/browserup/browserup-proxy/commit/4b38e7a3e20917e5c3329d0d4e9590bed9d578ab
- https://github.com/browserup/browserup-proxy/releases/tag/v2.1.2
- https://securitylab.github.com/research/bean-validation-RCE
