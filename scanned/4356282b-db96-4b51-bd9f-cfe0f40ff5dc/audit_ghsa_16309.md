# [C] DIRAC's TokenManager does not check permissions on cached tokens

## Summary
Severity: Critical
Advisory: GHSA-59qj-jcjv-662j
CVE: CVE-2024-24825
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-59qj-jcjv-662j
Type: github-advisory

## Affected
- PyPI: `DIRAC` — affected >=8.0.0 <8.0.37
- PyPI: `dirac` — affected >=0 <8.0.37

## Details
### Impact

Any user could get a token that has been requested by another user/agent

### Patches
The vulnerability is fixed in version 8.0.37.

### Workarounds

None

### References

## References
- https://github.com/DIRACGrid/DIRAC/security/advisories/GHSA-59qj-jcjv-662j
- https://nvd.nist.gov/vuln/detail/CVE-2024-24825
- https://github.com/DIRACGrid/DIRAC/commit/9487921684e2925b4cf72d6c423718cf4950f3fe
- https://github.com/DIRACGrid/DIRAC/commit/f9ddab755b9a69acb85e14d2db851d8ac0c9648c
- https://github.com/DIRACGrid/DIRAC
- https://github.com/pypa/advisory-database/tree/main/vulns/dirac/PYSEC-2024-125.yaml
