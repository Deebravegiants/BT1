# [M] UnsafeAccessor 1.4.0 until 1.7.0 has no security checking for UnsafeAccess.getInstance()

## Summary
Severity: Medium
Advisory: GHSA-cr6p-23cf-w9g9
CVE: CVE-2022-31139
CWE: CWE-200, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-12
Source: https://github.com/advisories/GHSA-cr6p-23cf-w9g9
Type: github-advisory

## Affected
- Maven: `io.github.karlatemp:unsafe-accessor` — affected >=1.4.0 <1.7.0

## Details
### Overview

Affected versions have no limit to using unsafe-accessor. Can be ignored if `SecurityCheck.AccessLimiter` not setup

### Details

If UA was loaded as a named module, the internal data of UA will be protected by JVM and others can only access UA via UA's standard api.
Main application can setup `SecurityCheck.AccessLimiter` for UA to limit accesses to UA.
Untrusted code can access UA without lmitation in affected versions even UA was loaded as a named module.

### References

[The commit to fix](https://github.com/Karlatemp/UnsafeAccessor/commit/4ef83000184e8f13239a1ea2847ee401d81585fd)

## References
- https://github.com/Karlatemp/UnsafeAccessor/security/advisories/GHSA-cr6p-23cf-w9g9
- https://nvd.nist.gov/vuln/detail/CVE-2022-31139
- https://github.com/Karlatemp/UnsafeAccessor/commit/4ef83000184e8f13239a1ea2847ee401d81585fd
- https://github.com/Karlatemp/UnsafeAccessor
- https://github.com/Karlatemp/UnsafeAccessor/releases/tag/1.7.0
