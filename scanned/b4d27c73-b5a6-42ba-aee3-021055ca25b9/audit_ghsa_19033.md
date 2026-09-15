# [C] pgAdmin4 vulnerable to Remote Code Execution (RCE) when running in server mode

## Summary
Severity: Critical
Advisory: GHSA-w2p4-p4rh-qcm3
CVE: CVE-2025-12762
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-w2p4-p4rh-qcm3
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.10

## Details
pgAdmin versions up to 9.9 are affected by a Remote Code Execution (RCE) vulnerability that occurs when running in server mode and performing restores from PLAIN-format dump files. This issue allows attackers to inject and execute arbitrary commands on the server hosting pgAdmin, posing a critical risk to the integrity and security of the database management system and underlying data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12762
- https://github.com/pgadmin-org/pgadmin4/issues/9320
- https://github.com/pgadmin-org/pgadmin4/commit/1d397395f75320ca1d4ed5e9ca721c603415e836
- https://github.com/pgadmin-org/pgadmin4
