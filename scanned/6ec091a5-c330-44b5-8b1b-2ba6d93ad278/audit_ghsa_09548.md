# [H] SQLFluff: Recursive Stack Overflow in Parser

## Summary
Severity: High
Advisory: GHSA-wmhf-fqc8-vxhh
CVE: CVE-2026-46373
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-wmhf-fqc8-vxhh
Type: github-advisory

## Affected
- PyPI: `sqlfluff` — affected >=0 <4.1.0

## Details
### Impact

In deployments where untrusted users can provide SQL queries to be linted, an untrusted user can submit a malicious query with deliberate excessive nesting to any application using the parser to trigger a Denial of Service through resource exhaustion.

### Patches

Versions 4.1.0 and up contain a configurable recursion limit, which is enabled by default, to prevent this manner of exploit.

### Credit

Ori Nakar from Imperva Threat Research Team.

## References
- https://github.com/sqlfluff/sqlfluff/security/advisories/GHSA-wmhf-fqc8-vxhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46373
- https://github.com/pypa/advisory-database/tree/main/vulns/sqlfluff/PYSEC-2026-209.yaml
- https://github.com/sqlfluff/sqlfluff
