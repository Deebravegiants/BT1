# [H] pgAdmin Cross-site Scripting vulnerability in /settings/store API response json payload

## Summary
Severity: High
Advisory: GHSA-xv64-8p4r-94gq
CVE: CVE-2024-4216
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-xv64-8p4r-94gq
Type: github-advisory

## Affected
- PyPI: `pgAdmin4` — affected >=0 <8.6

## Details
pgAdmin <= 8.5 is affected by XSS vulnerability in /settings/store API response json payload. This vulnerability allows attackers to execute malicious script at the client end.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4216
- https://github.com/pgadmin-org/pgadmin4/issues/7282
- https://github.com/pgadmin-org/pgadmin4/commit/e384c9665ae2e72376be7cefa8e652efcee93767
- https://github.com/pgadmin-org/pgadmin4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T2YFVCB4HCXU3FQBZ5XTWJZWSZUDNCXE
