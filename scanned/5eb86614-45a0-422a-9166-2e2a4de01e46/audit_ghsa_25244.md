# [M] Moodle cross-site scripting (XSS) vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-j6c3-3c4w-qv8p
CVE: CVE-2013-7341
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j6c3-3c4w-qv8p
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.4.9
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.5
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.2
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.14
- Packagist: `typo3/cms` — affected >=7.0.0 <7.3.1

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Flowplayer Flash before 3.2.17, as used in Moodle through 2.3.11, 2.4.x before 2.4.9, 2.5.x before 2.5.5, and 2.6.x before 2.6.2, allow remote attackers to inject arbitrary web script or HTML by (1) providing a crafted playerId or (2) referencing an external domain, a related issue to CVE-2013-7342.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7341
- https://github.com/flowplayer/flash/issues/121
- https://github.com/moodle/moodle/commit/98d135fea3006334093efa822205d4b2c3fd8ff9
- https://github.com/moodle/moodle/commit/9f2967e301d123d11625f3b6948e1ee538086791
- https://github.com/moodle/moodle/commit/c3cd5e1db9de4f1a634492d99990534e30518066
- https://github.com/moodle/moodle/commit/d65634044ebaa738f55bdec521beb42844d6916a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2013-7341.yaml
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=256420
- https://typo3.org/security/advisory/typo3-core-sa-2015-007
- http://flash.flowplayer.org/documentation/version-history.html
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-43344
- http://openwall.com/lists/oss-security/2014/03/17/1
