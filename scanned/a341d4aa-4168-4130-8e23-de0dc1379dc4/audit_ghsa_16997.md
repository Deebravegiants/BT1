# [M] Contao: Remember-me tokens will not be cleared after a password change

## Summary
Severity: Medium
Advisory: GHSA-r4r6-j2j3-7pp5
CVE: CVE-2024-30262
CWE: CWE-384, CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-r4r6-j2j3-7pp5
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=0 <4.13.40

## Details
### Impact

When a front end member changes their password, the corresponding remember-me tokens are not removed.

### Patches

Update to Contao 4.13.40.

### Workarounds

Disable "Allow auto login" in the login module.

### References

https://contao.org/en/security-advisories/remember-me-tokens-are-not-cleared-after-a-password-change

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-r4r6-j2j3-7pp5
- https://nvd.nist.gov/vuln/detail/CVE-2024-30262
- https://github.com/contao/contao/commit/3032baa456f607169ffae82a8920354adb338fe9
- https://contao.org/en/security-advisories/remember-me-tokens-are-not-cleared-after-a-password-change
- https://github.com/contao/contao
