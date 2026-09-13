# [H] simpleSAMLphp incorrectly handles XML encryption

## Summary
Severity: High
Advisory: GHSA-5fj7-f8x3-q2mc
CVE: CVE-2011-4625
CWE: CWE-755
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-5fj7-f8x3-q2mc
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <1.8.1

## Details
simplesamlphp before 1.6.3 (squeeze) and before 1.8.2 (sid) incorrectly handles XML encryption which could allow remote attackers to decrypt or forge messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4625
- https://github.com/simplesamlphp/simplesamlphp
- https://github.com/simplesamlphp/simplesamlphp/blob/b3059c51a915910c6631fb2ee597c0fb6ad9162b/docs/simplesamlphp-changelog-1.x.md?plain=1#L1624
- https://secure1.securityspace.com/smysecure/catid.html?in=DSA%202330-1
- https://security-tracker.debian.org/tracker/CVE-2011-4625
- https://www.mageni.net/vulnerability/debian-security-advisory-dsa-2330-1-simplesamlphp-70545
