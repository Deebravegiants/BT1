# [M] python-jose denial of service via compressed JWE content

## Summary
Severity: Medium
Advisory: GHSA-cjwg-qfpm-7377
CVE: CVE-2024-33664
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-26
Source: https://github.com/advisories/GHSA-cjwg-qfpm-7377
Type: github-advisory

## Affected
- PyPI: `python-jose` — affected >=0 <3.4.0

## Details
python-jose through 3.3.0 allows attackers to cause a denial of service (resource consumption) during a decode via a crafted JSON Web Encryption (JWE) token with a high compression ratio, aka a "JWT bomb." This is similar to CVE-2024-21319.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33664
- https://github.com/mpdavis/python-jose/issues/344
- https://github.com/mpdavis/python-jose/pull/345
- https://github.com/mpdavis/python-jose
- https://github.com/mpdavis/python-jose/releases/tag/3.4.0
- https://github.com/pypa/advisory-database/tree/main/vulns/python-jose/PYSEC-2024-233.yaml
- https://www.vicarius.io/vsociety/posts/jwt-bomb-in-python-jose-cve-2024-33664
