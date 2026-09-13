# [M] Malicious users could abuse Sydent to control the content of invitation emails

## Summary
Severity: Medium
Advisory: GHSA-mh74-4m5g-fcjx
CVE: CVE-2021-29432
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-mh74-4m5g-fcjx
Type: github-advisory

## Affected
- PyPI: `matrix-sydent` — affected >=0 <2.3.0

## Details
### Impact

A malicious user could abuse Sydent to send out arbitrary emails from the Sydent email address. This could be used to construct plausible phishing emails, for example.

### Patches

Fixed in 4469d1d, 6b405a8, 65a6e91.

Note that these patches include changes to the *default* email templates. If these templates have been locally modified, they must also be updated.

### For more information

If you have any questions or comments about this advisory, email us at security@matrix.org.

## References
- https://github.com/matrix-org/sydent/security/advisories/GHSA-mh74-4m5g-fcjx
- https://nvd.nist.gov/vuln/detail/CVE-2021-29432
- https://github.com/matrix-org/sydent/commit/4469d1d42b2b1612b70638224c07e19623039c42
- https://github.com/matrix-org/sydent/releases/tag/v2.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-sydent/PYSEC-2021-23.yaml
- https://pypi.org/project/matrix-sydent
