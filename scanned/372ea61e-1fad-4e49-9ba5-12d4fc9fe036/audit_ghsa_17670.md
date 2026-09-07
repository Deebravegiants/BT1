# [H] PowSyBl Core allows deserialization of untrusted SparseMatrix data

## Summary
Severity: High
Advisory: GHSA-f5cx-h789-j959
CVE: CVE-2025-47771
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-06-19
Source: https://github.com/advisories/GHSA-f5cx-h789-j959
Type: github-advisory

## Affected
- Maven: `com.powsybl:powsybl-math` — affected >=6.3.0 <6.7.2

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

This is a disclosure for a security vulnerability in the `SparseMatrix` class. The vulnerability is a deserialization issue that
can lead to a wide range of privilege escalations depending on the circumstances. The problematic area is the `read` method
of the `SparseMatrix` class.
This method takes in an `InputStream` and returns a `SparseMatrix` object. We consider this to be a method that can be
exposed to untrusted input in at least two use cases:
- A user can adopt this method in an application where users can submit an `InputStream` and the application parses it into
a `SparseMatrix`. This can be a multi-tenant application that hosts many different users perhaps with different privilege
levels.
- A user adopts the method for a local tool but receives the `InputStream` from external sources.

#### Am I impacted?
You are vulnerable if you import non-controlled serialized `SparseMatrix` objects.


### Patches
com.powsybl:powsybl-math:6.7.2 and higher


### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Do not use `SparseMatrix` deserialization (`SparseMatrix.read(...)` methods).

### References
[powsybl-core v6.7.2](https://github.com/powsybl/powsybl-core/releases/tag/v6.7.2)

## References
- https://github.com/powsybl/powsybl-core/security/advisories/GHSA-f5cx-h789-j959
- https://nvd.nist.gov/vuln/detail/CVE-2025-47771
- https://github.com/powsybl/powsybl-core/commit/8ed16ce41683c4aef5f6aa1dd5ae8642aa5ed2bd
- https://github.com/powsybl/powsybl-core
- https://github.com/powsybl/powsybl-core/releases/tag/v6.7.2
