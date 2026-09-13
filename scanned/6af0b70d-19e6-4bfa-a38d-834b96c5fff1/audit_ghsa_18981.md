# [M] pgAdmin 4 has command injection vulnerability on Windows systems

## Summary
Severity: Medium
Advisory: GHSA-rm79-x4g6-hvg5
CVE: CVE-2025-12763
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-rm79-x4g6-hvg5
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.10

## Details
pgAdmin 4 versions up to 9.9 are affected by a command injection vulnerability on Windows systems. This issue is caused by the use of shell=True during backup and restore operations, enabling attackers to execute arbitrary system commands by providing specially crafted file path input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12763
- https://github.com/pgadmin-org/pgadmin4/issues/9323
- https://github.com/pgadmin-org/pgadmin4/commit/e374edc69239b3e02ecde895e27d9f9e488b87ee
- https://github.com/pgadmin-org/pgadmin4
