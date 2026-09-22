# [H] Exposure of information in Action Pack

## Summary
Severity: High
Advisory: GHSA-wh98-p28r-vrc9
CVE: CVE-2022-23633
CWE: CWE-200, CWE-212
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-wh98-p28r-vrc9
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=5.0.0.0 <5.2.6.2
- RubyGems: `actionpack` — affected >=6.0.0.0 <6.0.4.6
- RubyGems: `actionpack` — affected >=6.1.0.0 <6.1.4.6
- RubyGems: `actionpack` — affected >=7.0.0.0 <7.0.2.2

## Details
### Impact

Under certain circumstances response bodies will not be closed, for example a [bug in a webserver](https://github.com/puma/puma/pull/2812) or a bug in a Rack middleware.  In the event a response is *not* notified of a `close`, `ActionDispatch::Executor` will not know to reset thread local state for the next request.  This can lead to data being leaked to subsequent requests, especially when interacting with `ActiveSupport::CurrentAttributes`.

Upgrading to the FIXED versions of Rails will ensure mitigation of this issue even in the context of a buggy webserver or middleware implementation.

### Patches

This has been fixed in Rails 7.0.2.2, 6.1.4.6, 6.0.4.6, and 5.2.6.2.

### Workarounds

Upgrading is highly recommended, but to work around this problem the following middleware can be used:

```ruby
class GuardedExecutor < ActionDispatch::Executor
  def call(env)
    ensure_completed!
    super
  end

  private

    def ensure_completed!
      @executor.new.complete! if @executor.active?
    end
end

# Ensure the guard is inserted before ActionDispatch::Executor
Rails.application.configure do
  config.middleware.swap ActionDispatch::Executor, GuardedExecutor, executor
end
```

## References
- https://github.com/rails/rails/security/advisories/GHSA-wh98-p28r-vrc9
- https://nvd.nist.gov/vuln/detail/CVE-2022-23633
- https://github.com/rails/rails/commit/f9a2ad03943d5c2ba54e1d45f155442b519c75da
- https://discuss.rubyonrails.org/t/cve-2022-23633-possible-exposure-of-information-vulnerability-in-action-pack/80016
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2022-23633.yml
- https://groups.google.com/g/ruby-security-ann/c/FkTM-_7zSNA/m/K2RiMJBlBAAJ
- https://lists.debian.org/debian-lts-announce/2022/09/msg00002.html
- https://rubyonrails.org/2022/2/11/Rails-7-0-2-2-6-1-4-6-6-0-4-6-and-5-2-6-2-have-been-released
- https://security.netapp.com/advisory/ntap-20240119-0013
- https://www.debian.org/security/2023/dsa-5372
- http://www.openwall.com/lists/oss-security/2022/02/11/5
