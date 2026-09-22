# [M] rdiffweb vulnerable to Special Element Injection

## Summary
Severity: Medium
Advisory: GHSA-83pm-7v48-5jp4
CVE: CVE-2022-4721
CWE: CWE-75
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-83pm-7v48-5jp4
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.5.5

## Details
In rdiffweb prior to 2.5.5, lack of sanitisation of characters in SSH key name could allow attacker to inject a hyperlink injection that could allow attacker to redirect victim to malicious websites.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4721
- https://github.com/ikus060/rdiffweb/commit/6afaae56a29536f0118b3380d296c416aa6d078d
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-43007.yaml
- https://huntr.dev/bounties/3c48ef5d-da4d-4ee4-aaca-af65e7273720
