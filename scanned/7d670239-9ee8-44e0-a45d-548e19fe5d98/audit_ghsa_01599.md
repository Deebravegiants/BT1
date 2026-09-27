# [H] Potential Remote Code Execution vulnerability

## Summary
Severity: High
Advisory: GHSA-8gv3-3j7f-wg94
CVE: CVE-2020-15227
CWE: CWE-74, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-10-02
Source: https://github.com/advisories/GHSA-8gv3-3j7f-wg94
Type: github-advisory

## Affected
- Packagist: `nette/application` — affected >=2.2.0 <2.2.10
- Packagist: `nette/application` — affected >=2.3.0 <2.3.14
- Packagist: `nette/application` — affected >=2.4.0 <2.4.16
- Packagist: `nette/application` — affected >=3.0.0 <3.0.6
- Packagist: `nette/application` — affected >=2.0.0 <2.0.19
- Packagist: `nette/application` — affected >=2.1.0 <2.1.13

## Details
Packages nette/application versions prior to 2.2.10, 2.3.14, 2.4.16, 3.0.6 and nette/nette versions prior to 2.0.19 and 2.1.13 are vulnerable to an code injection attack by passing specially formed parameters to URL that may possibly leading to RCE. 

Reported by Cyku Hong from DEVCORE (https://devco.re)

### Impact
Code injection, possible remote code execution.

### Patches
Fixed in nette/application 2.2.10, 2.3.14, 2.4.16, 3.0.6 and nette/nette 2.0.19 and 2.1.13

## References
- https://github.com/nette/application/security/advisories/GHSA-8gv3-3j7f-wg94
- https://nvd.nist.gov/vuln/detail/CVE-2020-15227
- https://blog.nette.org/en/cve-2020-15227-potential-remote-code-execution-vulnerability
- https://github.com/FriendsOfPHP/security-advisories/blob/master/nette/application/CVE-2020-15227.yaml
- https://github.com/nette/application
- https://lists.debian.org/debian-lts-announce/2021/04/msg00003.html
- https://packagist.org/packages/nette/application
- https://packagist.org/packages/nette/nette
