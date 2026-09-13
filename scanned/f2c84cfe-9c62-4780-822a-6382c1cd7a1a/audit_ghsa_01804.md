# [H] PHP file inclusion in the Sulu admin panel

## Summary
Severity: High
Advisory: GHSA-vx6j-pjrh-vgjh
CVE: CVE-2021-43836
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-15
Source: https://github.com/advisories/GHSA-vx6j-pjrh-vgjh
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=0 <1.6.44
- Packagist: `sulu/sulu` — affected >=2.0.0 <2.2.18
- Packagist: `sulu/sulu` — affected >=2.3.0 <2.3.8
- Packagist: `sulu/sulu` — affected >=2.4.0-RC1 <2.4.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

An attacker can read arbitrary local files via a PHP file include. In a default configuration this also leads to remote code execution.

* Compromised components: Arbitrary file read on the server, (Potential) Remote code execution
* Exploitation pre-requisite: User account on the backend

### Patches

_Has the problem been patched? What versions should users upgrade to?_

The problem is patched with the Versions 1.6.44, 2.2.18, 2.3.8, 2.4.0

### Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Overwrite the service `sulu_route.generator.expression_token_provider` and wrap the translator before passing it to the expression language. 

### References

_Are there any links users can visit to find out more?_

Currently not.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [example link to repo](http://example.com)
* Email us at [example email address](mailto:example@example.com)

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-vx6j-pjrh-vgjh
- https://nvd.nist.gov/vuln/detail/CVE-2021-43836
- https://github.com/sulu/sulu/commit/9c948f9ce350c68b53af8c3910e2cefc7f722b54
- https://github.com/sulu/sulu
