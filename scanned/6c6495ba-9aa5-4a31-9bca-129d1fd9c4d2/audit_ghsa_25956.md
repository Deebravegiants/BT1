# [C] Command Injection vulnerability in asciidoctor-include-ext

## Summary
Severity: Critical
Advisory: GHSA-v222-6mr4-qj29
CVE: CVE-2022-24803
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-v222-6mr4-qj29
Type: github-advisory

## Affected
- RubyGems: `asciidoctor-include-ext` — affected >=0 <0.4.0

## Details
### Impact

Applications using [Asciidoctor (Ruby)](https://github.com/asciidoctor/asciidoctor) with [asciidoctor-include-ext](https://github.com/jirutka/asciidoctor-include-ext) (prior to version 0.4.0), which render user-supplied input in AsciiDoc markup, may allow an attacker to execute arbitrary system commands on the host operating system. ~~This attack is possible even when `allow-uri-read` is disabled!~~ (EDIT: it’s not)


### Patches

The vulnerability has been fixed in commit c7ea001 (and further improved in cbaccf3), which is included in version [0.4.0](https://rubygems.org/gems/asciidoctor-include-ext/versions/0.4.0).

### Workarounds

```rb
require 'asciidoctor/include_ext'

class Asciidoctor::IncludeExt::IncludeProcessor
  # Overrides superclass private method to mitigate Command Injection
  # vulnerability in asciidoctor-include-ext <0.4.0.
  def target_uri?(target)
    target.downcase.start_with?('http://', 'https://') \
      && URI.parse(target).is_a?(URI::HTTP)
  rescue URI::InvalidURIError
    false
  end
end
```

### References

* https://sakurity.com/blog/2015/02/28/openuri.html

### Credits

This vulnerability was discovered by Joern Schneeweisz from the GitLab Security Research Team.


### For more information

See commit message c7ea001.

If you have any questions or comments about this advisory open an issue in [jirutka/asciidoctor-include-ext](https://github.com/jirutka/asciidoctor-include-ext/issues/).

## References
- https://github.com/jirutka/asciidoctor-include-ext/security/advisories/GHSA-v222-6mr4-qj29
- https://nvd.nist.gov/vuln/detail/CVE-2022-24803
- https://github.com/jirutka/asciidoctor-include-ext/commit/c7ea001a597c7033575342c51483dab7b87ae155
- https://github.com/jirutka/asciidoctor-include-ext/commit/cbaccf3de533cbca224bf61d0b74e4b84d41d8ee
- https://github.com/jirutka/asciidoctor-include-ext
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/asciidoctor-include-ext/CVE-2022-24803.yml
