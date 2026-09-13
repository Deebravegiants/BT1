# [M] Sulu Observable Response Discrepancy on Admin Login

## Summary
Severity: Medium
Advisory: GHSA-wmwf-49vv-p3mr
CVE: CVE-2023-39343
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-03
Source: https://github.com/advisories/GHSA-wmwf-49vv-p3mr
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=2.5.0 <2.5.10

## Details
### Impact

It allows over the Admin Login form to detect which user (username, email) exists and which one do not exist.

Impacted by this issue are Sulu installation >= 2.5.0 and <2.5.10 using the newer Symfony Security System which is default since Symfony 6.0 but can be enabled in Symfony 5.4. Sulu Installation not using the old Symfony 5.4 security System and previous version are not impacted by this Security issue.

### Patches

The problem has been patched in version 2.5.10. 

### Workarounds

Create a custom AuthenticationFailureHandler which does not return the `$exception->getMessage();` instead the `$exception->getMessageKey();`

### References

Currently no references.

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-wmwf-49vv-p3mr
- https://nvd.nist.gov/vuln/detail/CVE-2023-39343
- https://github.com/sulu/sulu/commit/5f6c98ba030b2005793e2dc647cc938937ea889b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sulu/sulu/CVE-2023-39343.yaml
- https://github.com/sulu/sulu
- https://github.com/sulu/sulu/releases/tag/2.5.10
