# [C] com.enonic.xp:lib-auth vulnerable to Session Fixation

## Summary
Severity: Critical
Advisory: GHSA-4m5p-5w5w-3jcf
CVE: CVE-2024-23679
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-4m5p-5w5w-3jcf
Type: github-advisory

## Affected
- Maven: `com.enonic.xp:lib-auth` — affected >=0 <7.7.4

## Details
### Impact
All id-providers using lib-auth `login` method.

### Patches
https://github.com/enonic/xp/commit/0189975691e9e6407a9fee87006f730e84f734ff
https://github.com/enonic/xp/commit/2abac31cec8679074debc4f1fb69c25930e40842
https://github.com/enonic/xp/commit/1f44674eb9ab3fbab7103e8d08067846e88bace4

### Workarounds
Don't use lib-auth for `login`. 
Java API uses low-level structures and allows to invalidate previous session before auth-info is added.

### References

https://github.com/enonic/xp/issues/9253

## References
- https://github.com/enonic/xp/security/advisories/GHSA-4m5p-5w5w-3jcf
- https://nvd.nist.gov/vuln/detail/CVE-2024-23679
- https://github.com/enonic/xp/issues/9253
- https://github.com/enonic/xp/commit/0189975691e9e6407a9fee87006f730e84f734ff
- https://github.com/enonic/xp/commit/1f44674eb9ab3fbab7103e8d08067846e88bace4
- https://github.com/enonic/xp/commit/2abac31cec8679074debc4f1fb69c25930e40842
- https://github.com/enonic/xp
- https://vulncheck.com/advisories/vc-advisory-GHSA-4m5p-5w5w-3jcf
