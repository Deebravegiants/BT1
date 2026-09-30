# [H] SQLFluff: Uncontrolled Resource Consumption in SQLFluff Parser

## Summary
Severity: High
Advisory: GHSA-73jc-5mrq-prw7
CVE: CVE-2026-46374
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-73jc-5mrq-prw7
Type: github-advisory

## Affected
- PyPI: `sqlfluff` — affected >=0 <4.2.0

## Details
### Impact

In deployments where untrusted users can provide SQL queries to be linted, an untrusted user can submit a malicious long query to any application using the parser to trigger a Denial of Service through resource exhaustion.

### Patches

Versions 4.2.0 and up contain a configurable parse node limit, which is enabled by default, to prevent this manner of exploit.

### Credit

Ori Nakar from Imperva Threat Research Team.

## References
- https://github.com/sqlfluff/sqlfluff/security/advisories/GHSA-73jc-5mrq-prw7
- https://nvd.nist.gov/vuln/detail/CVE-2026-46374
- https://github.com/pypa/advisory-database/tree/main/vulns/sqlfluff/PYSEC-2026-210.yaml
- https://github.com/sqlfluff/sqlfluff
