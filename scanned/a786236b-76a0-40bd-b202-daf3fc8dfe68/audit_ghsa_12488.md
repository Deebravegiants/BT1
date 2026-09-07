# [M] yiisoft/yii2-authclient's Oauth2 PKCE implementation is vulnerable

## Summary
Severity: Medium
Advisory: GHSA-rw54-6826-c8j5
CVE: CVE-2023-50714
CWE: CWE-287, CWE-347
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-rw54-6826-c8j5
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-authclient` — affected >=0 <2.2.15

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Original Report:

> The Oauth2 PKCE implementation is vulnerable in 2 ways:
> 1. The `authCodeVerifier` should be removed after usage (similar to 'authState')
> 2. There is a risk for a "downgrade attack" if PKCE is being relied on for CSRF protection.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

2.2.15

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

not known yet.

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/yiisoft/yii2-authclient/security/advisories/GHSA-rw54-6826-c8j5
- https://nvd.nist.gov/vuln/detail/CVE-2023-50714
- https://github.com/yiisoft/yii2-authclient/commit/721ed974bc44137437b0cdc8454e137fff8db213
- https://github.com/yiisoft/yii2-authclient
- https://github.com/yiisoft/yii2-authclient/blob/0d1c3880f4d79e20aa1d77c012650b54e69695ff/src/OAuth1.php#L158
- https://github.com/yiisoft/yii2-authclient/blob/0d1c3880f4d79e20aa1d77c012650b54e69695ff/src/OAuth2.php#L121
- https://github.com/yiisoft/yii2-authclient/blob/0d1c3880f4d79e20aa1d77c012650b54e69695ff/src/OpenIdConnect.php#L420
