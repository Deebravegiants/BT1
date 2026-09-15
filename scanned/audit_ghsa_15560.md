# [H] RestrictedPython information leakage via `AttributeError.obj` and the `string` module

## Summary
Severity: High
Advisory: GHSA-5rfv-66g4-jr8h
CVE: CVE-2024-47532
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-30
Source: https://github.com/advisories/GHSA-5rfv-66g4-jr8h
Type: github-advisory

## Affected
- PyPI: `RestrictedPython` — affected >=0 <7.3

## Details
### Impact
A user can gain access to protected (and potentially sensible) information indirectly via `AttributeError.obj` and the `string` module.

### Patches
The problem will be fixed in version 7.3.


### Workarounds
If the application does not require access to the module `string`, it can remove it from `RestrictedPython.Utilities.utility_builtins`  or otherwise do not make it available in the restricted execution environment.

## References
- https://github.com/zopefoundation/RestrictedPython/security/advisories/GHSA-5rfv-66g4-jr8h
- https://nvd.nist.gov/vuln/detail/CVE-2024-47532
- https://github.com/zopefoundation/RestrictedPython/commit/d701cc36cccac36b21fa200f1f2d1945a9a215e6
- https://github.com/pypa/advisory-database/tree/main/vulns/restrictedpython/PYSEC-2024-186.yaml
- https://github.com/zopefoundation/RestrictedPython
