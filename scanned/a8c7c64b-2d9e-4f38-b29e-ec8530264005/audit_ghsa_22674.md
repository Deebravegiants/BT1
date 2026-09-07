# [M] TYPO3 Flow Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vc74-c4m6-9979
CVE: CVE-2013-7082
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vc74-c4m6-9979
Type: github-advisory

## Affected
- Packagist: `neos/flow` — affected >=1.1.0 <1.1.1
- Packagist: `neos/flow` — affected >=2.0.0 <2.0.1
- Packagist: `typo3/flow` — affected >=1.1.0 <1.1.1
- Packagist: `typo3/flow` — affected >=2.0.0 <2.0.1

## Details
Cross-site scripting (XSS) vulnerability in the errorAction method in the ActionController base class in TYPO3 Flow (formerly FLOW3) 1.1.x before 1.1.1 and 2.0.x before 2.0.1 allows remote attackers to inject arbitrary web script or HTML via unspecified input, which is returned in an error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7082
- https://exchange.xforce.ibmcloud.com/vulnerabilities/89614
- https://github.com/FriendsOfPHP/security-advisories/blob/master/neos/flow/CVE-2013-7082.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/flow/CVE-2013-7082.yaml
- https://www.neos.io/blog/flow-sa-2013-001.html
- http://osvdb.org/100825
- http://secunia.com/advisories/55996
- http://typo3.org/teams/security/security-bulletins/typo3-flow/typo3-flow-sa-2013-001
