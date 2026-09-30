# [H] Uninitialized Variable in fastecdsa

## Summary
Severity: High
Advisory: GHSA-ph86-g9r3-5qw4
CVE: CVE-2024-21502
CWE: CWE-457, CWE-908
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-24
Source: https://github.com/advisories/GHSA-ph86-g9r3-5qw4
Type: github-advisory

## Affected
- PyPI: `fastecdsa` — affected >=0 <2.3.2

## Details
Versions of the package fastecdsa before 2.3.2 use an Uninitialized Variable on the stack, via the curvemath_mul function in src/curveMath.c, due to being used and interpreted as user-defined type. Depending on the variable's actual value it could be arbitrary free(), arbitrary realloc(), null pointer dereference and other. Since the stack can be controlled by the attacker, the vulnerability could be used to corrupt allocator structure, leading to possible heap exploitation. The attacker could cause denial of service by exploiting this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21502
- https://github.com/AntonKueltz/fastecdsa/commit/57fc5689c95d649dab7ef60cc99ac64589f01e36
- https://gist.github.com/keltecc/49da037072276f21b005a8337c15db26
- https://github.com/AntonKueltz/fastecdsa
- https://github.com/AntonKueltz/fastecdsa/blob/v2.3.1/src/curveMath.c%23L210
- https://security.snyk.io/vuln/SNYK-PYTHON-FASTECDSA-6262045
