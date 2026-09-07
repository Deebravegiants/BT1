# [M] Stored XSS using uppercase characters in HTMLEditor

## Summary
Severity: Medium
Advisory: GHSA-qw4w-vq8v-2wcv
CVE: CVE-2022-37430
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-qw4w-vq8v-2wcv
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.11.13

## Details
A malicious content author could add a Javascript payload to the href attribute of a link. A similar issue was identified and fixed via CVE-2022-28803. However, the fix didn't account for the casing of the href attribute. An attacker must have access to the CMS to exploit this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37430
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2022-37430.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-37430
