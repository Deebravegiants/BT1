# [M] sosreport Exposure of Sensitive Information vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7pf9-7cff-f854
CVE: CVE-2022-2806
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-02
Source: https://github.com/advisories/GHSA-7pf9-7cff-f854
Type: github-advisory

## Affected
- PyPI: `sosreport` — affected >=0 <4.4

## Details
It was found that the ovirt-log-collector/sosreport collects the RHV admin password unfiltered. Fixed in: sos-4.2-20.el8_6, ovirt-log-collector-4.4.7-2.el8ev

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2806
- https://github.com/sosreport/sos/pull/2947
- https://github.com/sosreport/sos/commit/5fd872c64c53af37015f366295e0c2418c969757
- https://github.com/sosreport/sos
