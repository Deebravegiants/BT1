# [M] pgAdmin 4: Stored cross-site scripting (XSS) vulnerability in Browser Tree and Explain Visualizer modules

## Summary
Severity: Medium
Advisory: GHSA-6p2c-69cv-3fxq
CVE: CVE-2026-7814
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-6p2c-69cv-3fxq
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.15

## Details
Stored cross-site scripting (XSS) vulnerability in pgAdmin 4 Browser Tree and Explain Visualizer modules.

User-controlled PostgreSQL object names (database, schema, table, column, etc.) were assigned to DOM elements via innerHTML, allowing crafted object names containing HTML markup to execute attacker-supplied JavaScript in the browser of any pgAdmin user who navigated to or executed EXPLAIN over the malicious object.

Fix replaces innerHTML with textContent.

This issue affects pgAdmin 4: before 9.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7814
- https://github.com/pgadmin-org/pgadmin4/issues/9865
- https://github.com/pgadmin-org/pgadmin4/pull/9865
- https://github.com/pgadmin-org/pgadmin4
