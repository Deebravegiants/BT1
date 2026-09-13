# [H] pgadmin4 affected by a Restore restriction bypass via key disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-3p7x-94q9-jq9x
CVE: CVE-2026-1707
CWE: CWE-284, CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-3p7x-94q9-jq9x
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.12

## Details
pgAdmin versions 9.11 are affected by a Restore restriction bypass via key disclosure vulnerability that occurs when running in server mode and performing restores from PLAIN-format dump files. An attacker with access to the pgAdmin web interface can observe an active restore operation, extract the `\restrict` key in real time, and race the restore process by overwriting the restore script with a payload that re-enables meta-commands using `\unrestrict <key>`. This results in reliable command execution on the pgAdmin host during the restore operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1707
- https://github.com/pgadmin-org/pgadmin4/issues/9518
- https://github.com/pgadmin-org/pgadmin4/commit/62e2d18b0261f88086db65059a6078db07169f18
- https://github.com/pgadmin-org/pgadmin4
