# [M] Access control vulnerable to user data deletion by anonynmous users

## Summary
Severity: Medium
Advisory: GHSA-g5vw-3h65-2q3v
CVE: CVE-2024-51734
CWE: CWE-269, CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-11-04
Source: https://github.com/advisories/GHSA-g5vw-3h65-2q3v
Type: github-advisory

## Affected
- PyPI: `AccessControl` — affected >=0 <7.2
- PyPI: `Zope` — affected >=0 <5.11.1

## Details
### Impact
Anonymous users can delete the user data maintained by an `AccessControl.userfolder.UserFolder` which may prevent any privileged access.

### Patches
The problem is fixed in version 7.2.

### Workarounds
The problem can be fixed by adding `data__roles__ = ()` to `AccessControl.userfolder.UserFolder`.

### References
https://github.com/zopefoundation/AccessControl/issues/159

## References
- https://github.com/zopefoundation/AccessControl/security/advisories/GHSA-g5vw-3h65-2q3v
- https://nvd.nist.gov/vuln/detail/CVE-2024-51734
- https://github.com/zopefoundation/AccessControl/issues/159
- https://github.com/zopefoundation/AccessControl
