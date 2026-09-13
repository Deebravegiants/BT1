# [C] Code injection in rope

## Summary
Severity: Critical
Advisory: GHSA-r38r-qp28-2m63
CVE: CVE-2014-3539
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-r38r-qp28-2m63
Type: github-advisory

## Affected
- PyPI: `rope` — affected >=0 <0.11.0

## Details
base/oi/doa.py in the Rope library in CPython (aka Python) allows remote attackers to execute arbitrary code by leveraging an unsafe call to pickle.load.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3539
- https://github.com/python-rope/rope/commit/b01da7aab5cd02129941d2a900e6e5e3b5f7d4fb
- https://bugzilla.redhat.com/show_bug.cgi?id=1116485
- https://github.com/pypa/advisory-database/tree/main/vulns/rope/PYSEC-2018-100.yaml
- https://github.com/python-rope/rope
- http://www.openwall.com/lists/oss-security/2015/02/07/1
