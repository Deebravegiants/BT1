# [H] pgAdmin Remote Code Execution (RCE) vulnerability

## Summary
Severity: High
Advisory: GHSA-27jx-ffw8-xrqv
CVE: CVE-2024-3116
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-04
Source: https://github.com/advisories/GHSA-27jx-ffw8-xrqv
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <8.5

## Details
pgAdmin <= 8.4 is affected by a  Remote Code Execution (RCE) vulnerability through the validate binary path API. This vulnerability allows attackers to execute arbitrary code on the server hosting PGAdmin, posing a severe risk to the database management system's integrity and the security of the underlying data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3116
- https://github.com/pgadmin-org/pgadmin4/issues/7326
- https://github.com/pgadmin-org/pgadmin4/commit/fbbbfe22dd468bcfef1e1f833ec32289a6e56a8b
- https://gist.github.com/aelmokhtar/689a8be7e3bd535ec01992d8ec7b2b98
- https://github.com/pgadmin-org/pgadmin4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GIF5T34JTTYRGIN5YPT366BDFG6452A2
- https://www.vicarius.io/vsociety/posts/remote-code-execution-vulnerability-in-pgadmin-cve-2024-3116
