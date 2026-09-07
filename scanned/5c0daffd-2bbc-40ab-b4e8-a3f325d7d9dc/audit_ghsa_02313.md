# [M] Cross-Site Scripting via Rich-Text Content

## Summary
Severity: Medium
Advisory: GHSA-c5c9-8c6m-727v
CVE: CVE-2021-32768
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-19
Source: https://github.com/advisories/GHSA-c5c9-8c6m-727v
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=7.0.0 <7.6.53
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.42
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.19
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.3.2
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.29
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.19
- Packagist: `typo3/cms` — affected >=11.0.0 <11.3.2
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.29
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.42
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.53

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC` (5.7)

### Problem
Failing to properly parse, sanitize and encode malicious rich-text content, the content rendering process in the website frontend is vulnerable to cross-site scripting. Corresponding rendering instructions via TypoScript functionality _[HTMLparser](https://docs.typo3.org/m/typo3/reference-typoscript/10.4/en-us/Functions/Htmlparser.html)_ do not consider all potentially malicious HTML tag & attribute combinations per default.

In addition, the lack of comprehensive default node configuration for rich-text fields in the backend user interface fosters this malfunction.

In default scenarios, a valid backend user account is needed to exploit this vulnerability. In case custom plugins used in the website frontend accept and reflect rich-text content submitted by users, no authentication is required.

### Solution
Update to TYPO3 versions 7.6.53 ELTS, 8.7.42 ELTS, 9.5.29, 10.4.19, 11.3.2 that fix the problem described above.

Custom package _[typo3/html-sanitizer](https://github.com/TYPO3/html-sanitizer)_ - based on allow-lists only - takes care of sanitizing potentially malicious markup. The default behavior is based on safe and commonly used markup - however, this can be extended or restricted further in case it is necessary for individual scenarios.

During the frontend rendering process, sanitization is applied to the default TypoScript path `lib.parseFunc`, which is implicitly used by the Fluid view-helper instruction `f:format.html`. Rich-text data persisted using the backend user interface is sanitized as well. Implementation details are explained in corresponding [ChangeLog documentation](https://docs.typo3.org/c/typo3/cms-core/master/en-us/Changelog/9.5.x/Important-94484-IntroduceHTMLSanitizer.html).

### Credits
Thanks to Benjamin Stiber, Gert-Jan Jansma, Gábor Ács-Kurucz, Alexander Kellner, Richie Lee, Nina Rösch who reported this issue, and to TYPO3 security team member Oliver Hader, as well as TYPO3 contributor Susanne Moog who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-013](https://typo3.org/security/advisory/typo3-core-sa-2021-013)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-c5c9-8c6m-727v
- https://github.com/TYPO3/typo3/security/advisories/GHSA-c5c9-8c6m-727v
- https://nvd.nist.gov/vuln/detail/CVE-2021-32768
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-32768.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-32768.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2021-013
