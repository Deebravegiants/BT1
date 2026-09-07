# [M] Typo3 Open Redirect In Frontend Rendering

## Summary
Severity: Medium
Advisory: GHSA-v6xv-rmqc-wcc8
CVE: CVE-2014-9508
CWE: CWE-59
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v6xv-rmqc-wcc8
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.39
- Packagist: `typo3/cms` — affected >=4.6.0 <6.2.9
- Packagist: `typo3/cms` — affected >=7.0.0 <7.0.2

## Details
The frontend rendering component in TYPO3 4.5.x before 4.5.39, 4.6.x through 6.2.x before 6.2.9, and 7.x before 7.0.2, allows remote attackers to change URLs to arbitrary domains.

An attacker could forge a request which modifies anchor only links on the homepage of a TYPO3 installation such that they point to arbitrary domains, if the configuration option `config.prefixLocalAnchors` is used with any possible value. TYPO3 versions 4.6.x and higher are only affected if the homepage is not a shortcut to a different page. As an additional pre-condition, URL rewriting must be enabled in the web server (which it typically is) when using extensions like realurl or cooluri.

Installations where `config.absRefPrefix` is additionally set to any value are not affected by this vulnerability.

Example of affected configuration:

```php
config.absRefPrefix =
config.prefixLocalAnchors = all 
page = PAGE 
page.10 = TEXT 
page.10.value = <a href="#skiplinks">Skiplinks</a> 
.htaccess:

RewriteCond %{REQUEST_FILENAME} !-f 
RewriteCond %{REQUEST_FILENAME} !-d 
RewriteCond %{REQUEST_FILENAME} !-l 
RewriteRule .* index.php [L] 
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9508
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2014-9508.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2014-003
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00106.html
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2014-003
