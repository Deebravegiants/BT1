# [M] Google Sign-In for Rails allowed redirects to malformed URLs

## Summary
Severity: Medium
Advisory: GHSA-7pwc-wh6m-44q3
CVE: CVE-2025-57821
CWE: CWE-601
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-27
Source: https://github.com/advisories/GHSA-7pwc-wh6m-44q3
Type: github-advisory

## Affected
- RubyGems: `google_sign_in` — affected >=0 <1.3.0

## Details
### Summary

It is possible to craft a malformed URL that passes the "same origin" check, resulting in the user being redirected to another origin.

### Details

The google_sign_in gem persists an optional URL for redirection after authentication. If this URL is malformed, it's possible for the user to be redirected to another origin after authentication, possibly resulting in exposure of authentication information such as the token.

Normally the value of this URL is only written and read by the library. If applications are configured to store session information in a database, there is no known vector to exploit this vulnerability. However, applications may be configured to store this information in a session cookie, in which case it may be chained with a session cookie attack to inject a crafted URL.

### Impact

Rails applications configured to store the `flash` information in a session cookie may be vulnerable, if this can be chained with an attack that allows injection of arbitrary data into the session cookie.

### Workarounds

If you are unable to upgrade this library, then you may mitigate the chained attack by explicitly setting `SameSite=Lax` or `SameSite=Strict` on the application session cookie.

### Credits

This issue was responsibly reported by Hackerone user [muntrive](https://hackerone.com/muntrive?type=user).

## References
- https://github.com/basecamp/google_sign_in/security/advisories/GHSA-7pwc-wh6m-44q3
- https://nvd.nist.gov/vuln/detail/CVE-2025-57821
- https://github.com/basecamp/google_sign_in/pull/73
- https://github.com/basecamp/google_sign_in/commit/85903651201257d4f14b97d4582e6d968ac32f15
- https://github.com/basecamp/google_sign_in/commit/a0548a604fb17e4eb1a57029f0d87e34e8499623
- https://github.com/basecamp/google_sign_in
- https://github.com/basecamp/google_sign_in/releases/tag/v1.3.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/google_sign_in/CVE-2025-57821.yml
