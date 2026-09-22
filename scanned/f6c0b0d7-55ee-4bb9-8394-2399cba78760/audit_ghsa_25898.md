# [H] Improper Authentication in FreeTAKServer

## Summary
Severity: High
Advisory: GHSA-hggv-mcp4-vxc5
CVE: CVE-2022-25508
CWE: CWE-287, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-hggv-mcp4-vxc5
Type: github-advisory

## Affected
- PyPI: `FreeTAKServer` — affected >=0 <1.9.8.5

## Details
FreeTAKServer is an open source, lightweight Server for connect TAK clients. An access control issue in the component /ManageRoute/postRoute of FreeTAKServer version 1.9.8 allows unauthenticated attackers to cause a Denial of Service (DoS) via an unusually large amount of created routes, or create unsafe or false routes for legitimate users. There is currently no known workaround. This issue was fixed in version 1.9.8.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25508
- https://github.com/FreeTAKTeam/FreeTakServer/issues/291
- https://github.com/FreeTAKTeam/FreeTakServer
- https://github.com/pypa/advisory-database/tree/main/vulns/freetakserver/PYSEC-2022-43054.yaml
