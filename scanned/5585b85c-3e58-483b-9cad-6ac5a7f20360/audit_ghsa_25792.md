# [H] Hard coded credentials in FreeTAKServer

## Summary
Severity: High
Advisory: GHSA-f897-875p-23x7
CVE: CVE-2022-25510
CWE: CWE-798
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-f897-875p-23x7
Type: github-advisory

## Affected
- PyPI: `FreeTAKServer` — affected >=0 <1.9.8.5

## Details
FreeTAKServer 1.9.8 contains a hardcoded Flask secret key which allows attackers to create crafted cookies to bypass authentication or escalate privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25510
- https://github.com/FreeTAKTeam/FreeTakServer/issues/292
- https://github.com/FreeTAKTeam/FreeTakServer
- https://github.com/pypa/advisory-database/tree/main/vulns/freetakserver/PYSEC-2022-43135.yaml
