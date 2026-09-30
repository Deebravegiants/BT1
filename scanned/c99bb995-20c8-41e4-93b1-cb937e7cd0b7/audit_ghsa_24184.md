# [M] sosreport sensitive information disclosure via weak permissions of the generated archives

## Summary
Severity: Medium
Advisory: GHSA-gw46-8559-cggp
CVE: CVE-2015-3171
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gw46-8559-cggp
Type: github-advisory

## Affected
- PyPI: `sosreport` — affected >=0 <3.3

## Details
sosreport 3.2 uses weak permissions for generated sosreport archives, which allows local users with access to `/var/tmp/` to obtain sensitive information by reading the contents of the archive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3171
- https://github.com/sosreport/sos/issues/425
- https://github.com/sosreport/sos/commit/d7759d3ddae5fe99a340c88a1d370d65cfa73fd6
- https://bugzilla.redhat.com/show_bug.cgi?id=1218658
- https://github.com/pypa/advisory-database/tree/main/vulns/sosreport/PYSEC-2017-72.yaml
- https://github.com/sosreport/sos
