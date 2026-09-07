# [H] Emmett has a path traversal in internal assets handler

## Summary
Severity: High
Advisory: GHSA-pr46-2v3c-5356
CVE: CVE-2026-39847
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-pr46-2v3c-5356
Type: github-advisory

## Affected
- PyPI: `emmett` — affected >=2.5.0 <2.8.1

## Details
The RSGI static handler for Emmett's internal assets (`/__emmett__` paths) is vulnerable to path traversal attacks.

An attacker can use `../` sequences (eg `/__emmett__/../rsgi/handlers.py`) to read arbitrary files outside the assets directory.

## References
- https://github.com/emmett-framework/emmett/security/advisories/GHSA-pr46-2v3c-5356
- https://nvd.nist.gov/vuln/detail/CVE-2026-39847
- https://github.com/emmett-framework/emmett
- https://github.com/pypa/advisory-database/tree/main/vulns/emmett/PYSEC-2026-59.yaml
