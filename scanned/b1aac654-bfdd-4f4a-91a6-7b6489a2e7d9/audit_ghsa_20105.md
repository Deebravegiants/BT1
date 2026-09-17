# [C] Multiple vulnerabilities in extension "Newsletter subscriber management" (fp_newsletter)

## Summary
Severity: Critical
Advisory: GHSA-f683-35w9-28g5
CVE: CVE-2022-47408
CWE: CWE-287, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-f683-35w9-28g5
Type: github-advisory

## Affected
- Packagist: `fixpunkt/fp-newsletter` — affected >=2.2.0 <3.2.6
- Packagist: `fixpunkt/fp-newsletter` — affected >=2.0.0 <2.1.2
- Packagist: `fixpunkt/fp-newsletter` — affected >=0 <1.1.1

## Details
The CAPTCHA of the extension can be bypassed which may result in automated creation of various newsletter subscribers. It is possible to provide arbitrary subscription UIDs to the `deleteAction` of the extension resulting in all newsletter subscribers to be unsubscribed. Insufficient access checks in the `createAction` and `unsubscribeAction` can be used to obtain data of existing newsletter subscribers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47408
- https://github.com/bihor/fp_newsletter/commit/bc673cd9ab04f3fdd1225303f2ccb378b11a3747
- https://github.com/FriendsOfPHP/security-advisories/blob/master/fixpunkt/fp-newsletter/CVE-2022-47408.yaml
- https://github.com/bihor/fp_newsletter
- https://typo3.org/security/advisory/typo3-ext-sa-2022-017
