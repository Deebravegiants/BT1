# [H] Possible DoS Vulnerability in Action Controller Token Authentication

## Summary
Severity: High
Advisory: GHSA-7wjx-3g7j-8584
CVE: CVE-2021-22904
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-05
Source: https://github.com/advisories/GHSA-7wjx-3g7j-8584
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.3.7
- RubyGems: `actionpack` — affected >=6.1.0 <6.1.3.2
- RubyGems: `actionpack` — affected >=5.2.5 <5.2.6
- RubyGems: `actionpack` — affected >=4.0.0 <5.2.4.6

## Details
There is a possible DoS vulnerability in the Token Authentication logic in Action Controller.

Versions Affected:  >= 4.0.0
Not affected:       < 4.0.0
Fixed Versions:     6.1.3.2, 6.0.3.7, 5.2.4.6, 5.2.6

Impact
------
Impacted code uses `authenticate_or_request_with_http_token` or `authenticate_with_http_token` for request authentication.  Impacted code will look something like this:

```
class PostsController < ApplicationController
  before_action :authenticate

  private

  def authenticate
    authenticate_or_request_with_http_token do |token, options|
      # ...
    end
  end
end
```

All users running an affected release should either upgrade or use one of the workarounds immediately.

Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
The following monkey patch placed in an initializer can be used to work around the issue:

```ruby
module ActionController::HttpAuthentication::Token
  AUTHN_PAIR_DELIMITERS = /(?:,|;|\t)/
end
```

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for the two supported release series. They are in git-am format and consist of a single changeset.

* 5-2-http-authentication-dos.patch - Patch for 5.2 series
* 6-0-http-authentication-dos.patch - Patch for 6.0 series
* 6-1-http-authentication-dos.patch - Patch for 6.1 series

Please note that only the 6.1.Z, 6.0.Z, and 5.2.Z series are supported at present. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases.

Credits
-------
Thank you to https://hackerone.com/wonda_tea_coffee for reporting this issue!

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22904
- https://hackerone.com/reports/1101125
- https://discuss.rubyonrails.org/t/cve-2021-22904-possible-dos-vulnerability-in-action-controller-token-authentication/77869
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v5.2.4.6
- https://github.com/rails/rails/releases/tag/v5.2.6
- https://github.com/rails/rails/releases/tag/v6.0.3.7
- https://github.com/rails/rails/releases/tag/v6.1.3.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2021-22904.yml
- https://groups.google.com/g/rubyonrails-security/c/Pf1TjkOBdyQ
- https://security.netapp.com/advisory/ntap-20210805-0009
