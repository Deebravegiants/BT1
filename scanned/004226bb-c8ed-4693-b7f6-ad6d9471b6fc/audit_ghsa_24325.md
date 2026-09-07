# [M] Typo3 Backend XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jg55-3q6h-2ccf
CVE: CVE-2009-0816
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-jg55-3q6h-2ccf
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=3.3.0
- Packagist: `typo3/cms` — affected >=4.0 <4.0.12
- Packagist: `typo3/cms` — affected >=4.1.0 <4.1.10
- Packagist: `typo3/cms` — affected >=4.2.0 <4.2.6
- Packagist: `typo3/cms` — affected 4.3alpha1

## Details
An Information Disclosure vulnerability in jumpUrl mechanism, used to track access on web pages and provided files, allows a remote attacker to read arbitrary files on a host.

The expected value of a mandatory hash secret, intended to invalidate such requests, is exposed to remote users allowing them to bypass access control by providing the correct value.

There's no authentication required to exploit this vulnerability. The vulnerability allows to read any file, the web server user account has access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0816
- https://web.archive.org/web/20210507104956/http://www.securitytracker.com/id?1021709
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-002
- http://www.debian.org/security/2009/dsa-1720
- http://www.openwall.com/lists/oss-security/2009/02/10/6
