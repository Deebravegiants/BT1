# [M] Devise has a confirmable "change email" race condition permits user to confirm email they have no access to

## Summary
Severity: Medium
Advisory: GHSA-57hq-95w6-v4fc
CVE: CVE-2026-32700
CWE: CWE-362
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-57hq-95w6-v4fc
Type: github-advisory

## Affected
- RubyGems: `devise` — affected >=0 <5.0.3

## Details
### Impact

A race condition in Devise's Confirmable module allows an attacker to confirm an email address they do not own. This affects any Devise application using the `reconfirmable` option (the default when using Confirmable with email changes).

By sending two concurrent email change requests, an attacker can desynchronize the `confirmation_token` and `unconfirmed_email` fields. The confirmation token is sent to an email the attacker controls, but the `unconfirmed_email` in the database points to a victim's email address. When the attacker uses the token, the victim's email is confirmed on the attacker's account.

### Patches

This is patched in Devise **v5.0.3**. Users should upgrade as soon as possible.

### Workarounds

Applications can override this specific method from Devise models to force `unconfirmed_email` to be persisted when unchanged: (assuming your model is `User`)

```ruby
class User < ApplicationRecord
  protected

  def postpone_email_change_until_confirmation_and_regenerate_confirmation_token
    unconfirmed_email_will_change!
    super
  end
end
```

Note: Mongoid does not seem to respect that `will_change!` should force the attribute to be persisted, even if it did not really change, so you might have to implement a workaround similar to Devise by setting `changed_attributes["unconfirmed_email"] = nil` as well.

## References
- https://github.com/heartcombo/devise/security/advisories/GHSA-57hq-95w6-v4fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-32700
- https://github.com/heartcombo/devise/issues/5783
- https://github.com/heartcombo/devise/pull/5784
- https://github.com/heartcombo/devise
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/devise/CVE-2026-32700.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/devise/GHSA-57hq-95w6-v4fc.yml
