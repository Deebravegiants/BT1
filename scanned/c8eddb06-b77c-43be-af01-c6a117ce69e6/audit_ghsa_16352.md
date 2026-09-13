# [M] Rails has possible Sensitive Session Information Leak in Active Storage

## Summary
Severity: Medium
Advisory: GHSA-8h22-8cf7-hq6g
CVE: CVE-2024-26144
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-8h22-8cf7-hq6g
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=5.2.0 <6.1.7.7
- RubyGems: `activestorage` — affected >=7.0.0 <7.0.8.1

## Details
# Possible Sensitive Session Information Leak in Active Storage

There is a possible sensitive session information leak in Active Storage.  By
default, Active Storage sends a `Set-Cookie` header along with the user's
session cookie when serving blobs.  It also sets `Cache-Control` to public.
Certain proxies may cache the Set-Cookie, leading to an information leak.

This vulnerability has been assigned the CVE identifier CVE-2024-26144.

Versions Affected:  >= 5.2.0, < 7.1.0
Not affected:       < 5.2.0, > 7.1.0
Fixed Versions:     7.0.8.1, 6.1.7.7

Impact
------
A proxy which chooses to caches this request can cause users to share
sessions. This may include a user receiving an attacker's session or vice
versa.

This was patched in 7.1.0 but not previously identified as a security
vulnerability.

All users running an affected release should either upgrade or use one of the
workarounds immediately.

Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
Upgrade to Rails 7.1.X, or configure caching proxies not to cache the
Set-Cookie headers.

Credits
-------

Thanks to [tyage](https://hackerone.com/tyage) for reporting this!

## References
- https://github.com/rails/rails/security/advisories/GHSA-8h22-8cf7-hq6g
- https://nvd.nist.gov/vuln/detail/CVE-2024-26144
- https://github.com/rails/rails/commit/723f54566023e91060a67b03353e7c03e7436433
- https://github.com/rails/rails/commit/78fe149509fac5b05e54187aaaef216fbb5fd0d3
- https://discuss.rubyonrails.org/t/possible-sensitive-session-information-leak-in-active-storage/84945
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2024-26144.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activestorage/CVE-2024-26144.yml
- https://security.netapp.com/advisory/ntap-20240510-0013
