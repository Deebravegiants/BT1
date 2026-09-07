# [M] Silverstripe Framework user enumeration via timing attack on login and password reset forms

## Summary
Severity: Medium
Advisory: GHSA-256q-hx8w-xcqx
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-256q-hx8w-xcqx
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <5.3.23

## Details
### Impact
User enumeration is possible by performing a timing attack on the login or password reset pages with user credentials.

This was originally disclosed in https://www.silverstripe.org/download/security-releases/ss-2017-005/ for CMS 3 but was not patched in CMS 4+

### References

- https://www.silverstripe.org/download/security-releases/ss-2017-005
- https://www.silverstripe.org/download/security-releases/ss-2025-001

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-256q-hx8w-xcqx
- https://nvd.nist.gov/vuln/detail/CVE-2017-12849
- https://github.com/silverstripe/silverstripe-framework/pull/11681
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2025-001.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2017-005
- https://www.silverstripe.org/download/security-releases/ss-2025-001
