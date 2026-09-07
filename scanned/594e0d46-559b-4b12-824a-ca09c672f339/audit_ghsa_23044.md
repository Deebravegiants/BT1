# [M] Firefly III vulnerable to stored XSS

## Summary
Severity: Medium
Advisory: GHSA-9xmx-rj7j-fv9q
CVE: CVE-2019-13644
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9xmx-rj7j-fv9q
Type: github-advisory

## Affected
- Packagist: `grumpydictator/firefly-iii` — affected >=0 <4.7.17.1

## Details
Firefly III before 4.7.17.1 is vulnerable to stored XSS due to lack of filtration of user-supplied data in a budget name. The JavaScript code is contained in a transaction, and is executed on the tags/show/$tag_number$ tag summary page. NOTE: It is asserted that an attacker must have the same access rights as the user in order to be able to execute the vulnerability

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13644
- https://github.com/firefly-iii/firefly-iii/issues/2335
- https://github.com/firefly-iii/firefly-iii/commit/def307010c388c4e92d7066671ad62e477cc087a
- https://github.com/firefly-iii/firefly-iii
- https://github.com/firefly-iii/firefly-iii/compare/76aa8ac...45b8c36
