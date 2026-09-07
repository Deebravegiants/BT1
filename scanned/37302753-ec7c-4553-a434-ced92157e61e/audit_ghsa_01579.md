# [H] Ensure that doorkeeper_token is valid when authenticating requests in API v2 calls

## Summary
Severity: High
Advisory: GHSA-f8cm-364f-q9qh
CVE: CVE-2020-15269
CWE: CWE-287, CWE-613
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-10-20
Source: https://github.com/advisories/GHSA-f8cm-364f-q9qh
Type: github-advisory

## Affected
- RubyGems: `spree` — affected >=0 <3.7.11
- RubyGems: `spree` — affected >=4.0.0 <4.0.4
- RubyGems: `spree` — affected >=4.1.0 <4.1.11

## Details
### Impact
The perpetrator who previously obtained an old expired user token could use it to access Storefront API v2 endpoints. 

### Patches
Please upgrade to 3.7.11, 4.0.4, or 4.1.11 depending on your used Spree version. 

### Workarounds
In your project directory create a decorator file `app/controllers/spree/api/v2/base_controller_decotatror.rb` with contents:

```ruby
module Spree
  module Api
    module V2
      module BaseControllerDecorator
        private

        def spree_current_user
          return nil unless doorkeeper_token
          return @spree_current_user if @spree_current_user

          doorkeeper_authorize!

          @spree_current_user ||= ::Spree.user_class.find_by(id: doorkeeper_token.resource_owner_id)
        end
     end
  end
end

Spree::Api::V2::BaseController.prepend(Spree::Api::V2::BaseControllerDecorator)
```

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@spreecommerce.org](mailto:security@spreecommerce.org)

## References
- https://github.com/spree/spree/security/advisories/GHSA-f8cm-364f-q9qh
- https://nvd.nist.gov/vuln/detail/CVE-2020-15269
- https://github.com/spree/spree/commit/e43643abfe51f54bd9208dd02298b366e9b9a847
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree/CVE-2020-15269.yml
- https://github.com/spree/spree
