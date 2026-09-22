# [H] TurboBoost Commands vulnerable to arbitrary method invocation

## Summary
Severity: High
Advisory: GHSA-mp76-7w5v-pr75
CVE: CVE-2024-28181
CWE: CWE-74
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-mp76-7w5v-pr75
Type: github-advisory

## Affected
- RubyGems: `turbo_boost-commands` — affected >=0 <0.1.3
- RubyGems: `turbo_boost-commands` — affected >=0.2.0 <0.2.2
- npm: `@turbo-boost/commands` — affected >=0 <0.1.3
- npm: `@turbo-boost/commands` — affected >=0.2.0 <0.2.2

## Details
### Impact
TurboBoost Commands has existing protections in place to guarantee that only public methods on Command classes can be invoked; however, the existing checks aren't as robust as they should be. It's possible for a sophisticated attacker to invoke more methods than should be permitted depending on the the strictness of authorization checks that individual applications enforce. Being able to call some of these methods can have security implications.

#### Details
Commands verify that the class must be a `Command` and that the method requested is defined as a public method; however, this isn't robust enough to guard against all unwanted code execution. The library should more strictly enforce which methods are considered safe before allowing them to be executed.  

### Patches
Patched in the following versions.
- 0.1.3
  - [NPM Package](https://www.npmjs.com/package/@turbo-boost/commands/v/0.1.3)
  - [Ruby GEM](https://rubygems.org/gems/turbo_boost-commands/versions/0.1.3)
- 0.2.2
  - [NPM Package](https://www.npmjs.com/package/@turbo-boost/commands/v/0.2.2)
  - [Ruby GEM](https://rubygems.org/gems/turbo_boost-commands/versions/0.2.2)


### Workarounds
You can add this guard to mitigate the issue if running an unpatched version of the library.

```ruby
class ApplicationCommand < TurboBoost::Commands::Command
  before_command do
    method_name = params[:name].include?("#") ? params[:name].split("#").last : :perform
    ancestors = self.class.ancestors[0..self.class.ancestors.index(TurboBoost::Commands::Command) - 1]
    allowed = ancestors.any? { |a| a.public_instance_methods(false).any? method_name.to_sym }
    throw :abort unless allowed # ← blocks invocation
    # raise "Invalid Command" unless allowed # ← blocks invocation
  end
end
```

## References
- https://github.com/hopsoft/turbo_boost-commands/security/advisories/GHSA-mp76-7w5v-pr75
- https://nvd.nist.gov/vuln/detail/CVE-2024-28181
- https://github.com/hopsoft/turbo_boost-commands/commit/337cda7d9222f1f449905454a7374222017a7477
- https://github.com/hopsoft/turbo_boost-commands/commit/88af4fc0ac39cc1799d16c49fab52f6dfbcec9ba
- https://github.com/hopsoft/turbo_boost-commands
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/turbo_boost-commands/CVE-2024-28181.yml
