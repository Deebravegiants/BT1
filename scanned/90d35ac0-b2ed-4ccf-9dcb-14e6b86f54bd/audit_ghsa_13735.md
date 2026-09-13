# [H] HTTPie allows attackers to eavesdrop on communications between the host and server via a man-in-the-middle attack

## Summary
Severity: High
Advisory: GHSA-8r96-8889-qg2x
CVE: CVE-2023-48052
CWE: CWE-295, CWE-599
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-8r96-8889-qg2x
Type: github-advisory

## Affected
- PyPI: `httpie` — affected >=0 <3.2.3

## Details
Missing SSL certificate validation in HTTPie v3.2.2 allows attackers to eavesdrop on communications between the host and server via a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48052
- https://github.com/httpie/cli/issues/1549
- https://github.com/httpie/cli/commit/7f03c52d2237440c5a672296ce6955aae4ed4f09
- https://github.com/httpie/cli
- https://github.com/httpie/cli/blob/master/httpie/client.py#L33
- https://github.com/httpie/cli/blob/master/httpie/internal/update_warnings.py#L44
- https://github.com/pypa/advisory-database/tree/main/vulns/httpie/PYSEC-2023-242.yaml
- https://gxx777.github.io/HTTPie_3.2.2_Cryptographic_API_Misuse_Vulnerability.md
