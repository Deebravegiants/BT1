# [M] Trac missing Content-Disposition HTTP header

## Summary
Severity: Medium
Advisory: GHSA-7jjr-3r8r-9pcf
CVE: CVE-2007-1406
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-7jjr-3r8r-9pcf
Type: github-advisory

## Affected
- PyPI: `trac` — affected >=0 <0.10.3.1

## Details
Trac before 0.10.3.1 does not send a Content-Disposition HTTP header specifying an attachment in certain "unsafe" situations, which has unknown impact and remote attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-1406
- https://github.com/pypa/advisory-database/tree/main/vulns/trac/PYSEC-2007-3.yaml
- http://trac.edgewall.org/wiki/ChangeLog
