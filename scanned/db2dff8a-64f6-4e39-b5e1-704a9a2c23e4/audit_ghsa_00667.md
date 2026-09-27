# [H] omniauth-apple allows attacker to fake their email address during authentication

## Summary
Severity: High
Advisory: GHSA-49r3-2549-3633
CVE: CVE-2020-26254
CWE: CWE-290
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-12-08
Source: https://github.com/advisories/GHSA-49r3-2549-3633
Type: github-advisory

## Affected
- RubyGems: `omniauth-apple` — affected >=0 <1.0.1

## Details
### Impact

This vulnerability impacts applications using the [omniauth-apple](https://github.com/nhosoya/omniauth-apple) strategy of OmniAuth and using the `info.email` field of OmniAuth's [Auth Hash Schema](https://github.com/omniauth/omniauth/wiki/Auth-Hash-Schema) for any kind of identification.  The value of this field may be set to any value of the attacker's choice including email addresses of other users.

For example, an application using omniauth-apple with the following code will be impacted:
```ruby
def omniauth_callback
    auth_hash = request.env['omniauth.auth']
    @authenticated_user = User.find_by(email: auth_hash.info.email)
end
```

Applications not using `info.email` for identification but are instead using the `uid` field are not impacted in the same manner.  Note, these applications may still be negatively affected if the value of `info.email` is being used for other purposes.

### Patches

Applications using affected versions of omniauth-apple are advised to upgrade to omniauth-apple version 1.0.1 or later.

### Workarounds

If unable to upgrade to a patched version, monkey patching `OmniAuth::Strategies::Apple#email` as follows is advised as a workaround:

```ruby
module OmniAuth
  module Strategies
    class Apple
      def email
        id_info['email']
      end
    end
  end
end
```

## References
- https://github.com/nhosoya/omniauth-apple/security/advisories/GHSA-49r3-2549-3633
- https://nvd.nist.gov/vuln/detail/CVE-2020-26254
- https://github.com/nhosoya/omniauth-apple/commit/b37d5409213adae2ca06a67fec14c8d3d07d9016
- https://github.com/nhosoya/omniauth-apple
- https://github.com/nhosoya/omniauth-apple/blob/master/CHANGELOG.md#101---2020-12-03
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/omniauth-apple/CVE-2020-26254.yml
