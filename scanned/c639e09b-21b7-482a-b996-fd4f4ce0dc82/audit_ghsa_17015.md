# [M] zenml Session Fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g3r5-72hf-p7p2
CVE: CVE-2024-2260
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-g3r5-72hf-p7p2
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0 <0.56.2

## Details
A session fixation vulnerability exists in the zenml-io/zenml application, where JWT tokens used for user authentication are not invalidated upon logout. This flaw allows an attacker to bypass authentication mechanisms by reusing a victim's JWT token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2260
- https://github.com/zenml-io/zenml/commit/68bcb3ba60cba9729c9713a49c39502d40fb945e
- https://github.com/pypa/advisory-database/tree/main/vulns/zenml/PYSEC-2024-254.yaml
- https://github.com/zenml-io/zenml
- https://huntr.com/bounties/2d0856ec-ed73-477a-8ea2-d5d4f15cf167
