# [M] SimpleSAMLphp Open redirection protection bypass

## Summary
Severity: Medium
Advisory: GHSA-2qfc-48v5-4w5h
CVE: CVE-2018-6520
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2qfc-48v5-4w5h
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <1.15.2

## Details
SimpleSAMLphp before 1.15.2 allows remote attackers to bypass an open redirect protection mechanism via crafted authority data in a URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6520
- https://github.com/simplesamlphp/simplesamlphp/issues/1473
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2018-6520.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://simplesamlphp.org/security/201801-02
