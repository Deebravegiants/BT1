# [M] Verification check bypass in Gate One

## Summary
Severity: Medium
Advisory: GHSA-q6j2-g8qf-wvf7
CVE: CVE-2020-19003
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-q6j2-g8qf-wvf7
Type: github-advisory

## Affected
- PyPI: `gateone` — affected >=0

## Details
An issue in Gate One 1.2.0 allows attackers to bypass to the verification check done by the origins list and connect to Gate One instances used by hosts not on the origins list.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-19003
- https://github.com/liftoff/GateOne/issues/728
- https://github.com/advisories/GHSA-q6j2-g8qf-wvf7
- https://github.com/liftoff/GateOne
- https://github.com/pypa/advisory-database/tree/main/vulns/gateone/PYSEC-2021-423.yaml
