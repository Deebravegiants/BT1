# [H] SSRF in Kitodo.Presentation

## Summary
Severity: High
Advisory: GHSA-x832-r2rj-4g5p
CVE: CVE-2022-24980
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-20
Source: https://github.com/advisories/GHSA-x832-r2rj-4g5p
Type: github-advisory

## Affected
- Packagist: `kitodo/presentation` — affected >=0 <2.3.2
- Packagist: `kitodo/presentation` — affected >=3.0.0 <3.2.3
- Packagist: `kitodo/presentation` — affected >=3.3.0 <3.3.4

## Details
An issue was discovered in the Kitodo.Presentation (aka dlf) extension before 2.3.2, 3.x before 3.2.3, and 3.3.x before 3.3.4 for TYPO3. A missing access check in an eID script allows an unauthenticated user to submit arbitrary URLs to this component. This results in SSRF, allowing attackers to view the content of any file or webpage the webserver has access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24980
- https://github.com/kitodo/kitodo-presentation/commit/059be3f82b08c60cbb798986cd3ff22dbf60a5e4
- https://github.com/kitodo/kitodo-presentation/commit/4a20621afc30778ba3b045be5110353cf4fd4fd4
- https://github.com/kitodo/kitodo-presentation/commit/9700478b46445f562c3e2051d61565d779f59275
- https://security.snyk.io/vuln/SNYK-PHP-KITODOPRESENTATION-2407280
- https://typo3.org/help/security-advisories
- https://typo3.org/security/advisory/typo3-ext-sa-2022-001
