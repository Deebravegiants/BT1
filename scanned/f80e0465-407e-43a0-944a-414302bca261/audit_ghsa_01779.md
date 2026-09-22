# [H] Missing Token Replay Detection in Saml2 Authentication services for ASP.NET

## Summary
Severity: High
Advisory: GHSA-g6j2-ch25-5mmv
CVE: CVE-2020-5261
CWE: CWE-294
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-03-25
Source: https://github.com/advisories/GHSA-g6j2-ch25-5mmv
Type: github-advisory

## Affected
- NuGet: `Sustainsys.Saml2` — affected >=2.0.0 <2.5.0

## Details
### Impact
Token Replay Detection is an important defence in depth measure for Single Sign On solutions. In all previous 2.X versions, the Token Replay Detection is not properly implemented. 

Note that version 1.0.1 is not affected. It has a correct Token Replay Implementation and is safe to use.

### Patches
The 2.5.0 version is patched.

### Workarounds
There are no workarounds with existing versions. Fixing the issue requires code updates.

### References
https://en.wikipedia.org/wiki/Replay_attack

### For more information
If you have any questions or comments about this advisory:
* Comment on #711.
* Email us at [security@sustainsys.com](mailto:security@susatinsys.com) if you think that there are further security issues.

## References
- https://github.com/Sustainsys/Saml2/security/advisories/GHSA-g6j2-ch25-5mmv
- https://nvd.nist.gov/vuln/detail/CVE-2020-5261
- https://github.com/Sustainsys/Saml2/issues/711
- https://github.com/Sustainsys/Saml2/commit/e58e0a1aff2b1ead6aca080b7cdced55ee6d5241
