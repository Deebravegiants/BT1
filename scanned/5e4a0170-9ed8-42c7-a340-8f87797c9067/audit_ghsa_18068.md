# [M] Google Sign-In for Rails allowed redirect to protocol-relative URI

## Summary
Severity: Medium
Advisory: GHSA-5jch-xhw4-r43v
CVE: CVE-2025-58067
CWE: CWE-601
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-5jch-xhw4-r43v
Type: github-advisory

## Affected
- RubyGems: `google_sign_in` — affected >=0 <1.3.1

## Details
## Summary

It is possible to redirect a user to another origin if the "proceed_to" value in the session store is set to a protocol-relative URL.

## Details

The google_sign_in gem persists an optional URL for redirection after authentication. If this URL is set to a protocol-relative URL, it improperly passes the "same origin" check, and it's possible for the user to be redirected to another origin after authentication, possibly resulting in exposure of authentication information if this attack is chained with other attacks.

Normally the value of this URL is only written and read by the library or the calling application. However, it may be possible to set this session value from a malicious site with a form submission.

## Impact

Any Rails applications using the google_sign_in gem may be vulnerable, if this vector can be chained with another attack that is able to modify the OAuth2 request parameters.

## Workarounds

No known workarounds.

## Credits

This issue was responsibly reported by Hackerone user [muntrive](https://hackerone.com/muntrive?type=user).

## References
- https://github.com/basecamp/google_sign_in/security/advisories/GHSA-5jch-xhw4-r43v
- https://nvd.nist.gov/vuln/detail/CVE-2025-58067
- https://github.com/basecamp/google_sign_in/pull/75
- https://github.com/basecamp/google_sign_in/commit/e97aef4626b1bcbd2c6f01f7dd25f12ac855d4cc
- https://github.com/basecamp/google_sign_in
- https://github.com/basecamp/google_sign_in/releases/tag/v1.3.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/google_sign_in/CVE-2025-58067.yml
