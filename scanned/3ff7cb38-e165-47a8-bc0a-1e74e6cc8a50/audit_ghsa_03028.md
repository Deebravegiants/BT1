# [H] Code Injection vulnerability in CarrierWave::RMagick

## Summary
Severity: High
Advisory: GHSA-cf3w-g86h-35x4
CVE: CVE-2021-21305
CWE: CWE-74, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2021-02-08
Source: https://github.com/advisories/GHSA-cf3w-g86h-35x4
Type: github-advisory

## Affected
- RubyGems: `carrierwave` — affected >=0 <1.3.2
- RubyGems: `carrierwave` — affected >=2.0.0 <2.1.1

## Details
### Impact
[CarrierWave::RMagick](https://github.com/carrierwaveuploader/carrierwave/blob/master/lib/carrierwave/processing/rmagick.rb) has a Code Injection vulnerability. Its `#manipulate!` method inappropriately evals the content of mutation option(`:read`/`:write`), allowing attackers to craft a string that can be executed as a Ruby code.
If an application developer supplies untrusted inputs to the option, it will lead to remote code execution(RCE).

(But supplying untrusted input to the option itself is dangerous even in absence of this vulnerability, since is prone to DoS vulnerability - attackers can try to consume massive amounts of memory by resizing to a very large dimension)

### Proof of Concept
```ruby
class MyUploader < CarrierWave::Uploader::Base
  include CarrierWave::RMagick
end

MyUploader.new.manipulate!({ read: { density: "1 }; p 'Hacked'; {" }}) # => shows "Hacked"
```

### Patches
Upgrade to [2.1.1](https://rubygems.org/gems/carrierwave/versions/2.1.1) or [1.3.2](https://rubygems.org/gems/carrierwave/versions/1.3.2).

### Workarounds
Stop supplying untrusted input to `#manipulate!`'s mutation option.

### References
[Code Injection Software Attack](https://owasp.org/www-community/attacks/Code_Injection)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [CarrierWave repo](https://github.com/carrierwaveuploader/carrierwave)
* Email me at [mit.shibuya@gmail.com](mailto:mit.shibuya@gmail.com)

## References
- https://github.com/carrierwaveuploader/carrierwave/security/advisories/GHSA-cf3w-g86h-35x4
- https://nvd.nist.gov/vuln/detail/CVE-2021-21305
- https://github.com/carrierwaveuploader/carrierwave/commit/387116f5c72efa42bc3938d946b4c8d2f22181b7
- https://github.com/carrierwaveuploader/carrierwave
- https://github.com/carrierwaveuploader/carrierwave/blob/master/CHANGELOG.md#132---2021-02-08
- https://github.com/carrierwaveuploader/carrierwave/blob/master/CHANGELOG.md#211---2021-02-08
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/carrierwave/CVE-2021-21305.yml
- https://rubygems.org/gems/carrierwave
