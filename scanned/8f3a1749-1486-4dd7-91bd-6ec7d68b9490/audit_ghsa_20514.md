# [H] Incorrect Comparison in cvxopt

## Summary
Severity: High
Advisory: GHSA-8rh6-h94m-vj54
CVE: CVE-2021-41500
CWE: CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-07
Source: https://github.com/advisories/GHSA-8rh6-h94m-vj54
Type: github-advisory

## Affected
- PyPI: `cvxopt` — affected >=0 <1.2.7

## Details
Incomplete string comparison vulnerability exits in cvxopt.org cvxop <= 1.2.6 in APIs (cvxopt.cholmod.diag, cvxopt.cholmod.getfactor, cvxopt.cholmod.solve, cvxopt.cholmod.spsolve), which allows attackers to conduct Denial of Service attacks by construct fake Capsule objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41500
- https://github.com/cvxopt/cvxopt/issues/193
- https://github.com/cvxopt/cvxopt/commit/d5a21cf1da62e4269176384b1ff62edac5579f94
- https://github.com/advisories/GHSA-8rh6-h94m-vj54
- https://github.com/cvxopt/cvxopt
- https://github.com/pypa/advisory-database/tree/main/vulns/cvxopt/PYSEC-2021-870.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CXTPM3DGVYTYQ54OFCMXZVWVOMR7JM2D
