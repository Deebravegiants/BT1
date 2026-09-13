# [M] Missing security headers in Action Pack on non-HTML responses

## Summary
Severity: Medium
Advisory: GHSA-fwhr-88qx-h9g7
CVE: CVE-2024-28103
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-fwhr-88qx-h9g7
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=6.1.0 <6.1.7.8
- RubyGems: `actionpack` — affected >=7.0.0 <7.0.8.4
- RubyGems: `actionpack` — affected >=7.1.0 <7.1.3.4
- RubyGems: `actionpack` — affected >=7.2.0.beta1 <7.2.0.beta2

## Details
# Permissions-Policy is Only Served on HTML Content-Type

The application configurable Permissions-Policy is only served on responses
with an HTML related Content-Type.

This has been assigned the CVE identifier CVE-2024-28103.


Versions Affected:  >= 6.1.0
Not affected:       < 6.1.0
Fixed Versions:     6.1.7.8, 7.0.8.4, and 7.1.3.4

Impact
------
Responses with a non-HTML Content-Type are not serving the configured Permissions-Policy. There are certain non-HTML Content-Types that would benefit from having the Permissions-Policy enforced.


Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
N/A

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for
the supported release series in accordance with our 
[maintenance policy](https://guides.rubyonrails.org/maintenance_policy.html#security-issues)
regarding security issues. They are in git-am format and consist of a
single changeset.

* 6-1-include-permissions-policy-header-on-non-html.patch - Patch for 6.1 series
* 7-0-include-permissions-policy-header-on-non-html.patch - Patch for 7.0 series
* 7-1-include-permissions-policy-header-on-non-html.patch - Patch for 7.1 series



Credits
-------

Thank you [shinkbr](https://hackerone.com/shinkbr) for reporting this!

## References
- https://github.com/rails/rails/security/advisories/GHSA-fwhr-88qx-h9g7
- https://nvd.nist.gov/vuln/detail/CVE-2024-28103
- https://github.com/rails/rails/commit/35858f1d9d57f6c4050a8d9ab754bd5d088b4523
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2024-28103.yml
- https://security.netapp.com/advisory/ntap-20241206-0002
