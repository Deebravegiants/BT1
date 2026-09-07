# [M] Cross site scripting vulnerability in ActionView

## Summary
Severity: Medium
Advisory: GHSA-65cv-r6x7-79hv
CVE: CVE-2020-5267
CWE: CWE-80
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-03-19
Source: https://github.com/advisories/GHSA-65cv-r6x7-79hv
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=0 <5.2.4.2
- RubyGems: `actionview` — affected >=6.0.0 <6.0.2.2

## Details
There is a possible cross site scripting (XSS) vulnerability in ActionView's JavaScript literal escape helpers.  Views that use the `j` or `escape_javascript` methods may be susceptible to XSS attacks.

### Impact

There is a possible XSS vulnerability in the `j` and `escape_javascript` methods in ActionView.  These methods are used for escaping JavaScript string literals.  Impacted code will look something like this:

```erb
<script>let a = `<%= j unknown_input %>`</script>
```

or

```erb
<script>let a = `<%= escape_javascript unknown_input %>`</script>
```

### Releases

The 6.0.2.2 and 5.2.4.2 releases are available at the normal locations.

### Workarounds

For those that can't upgrade, the following monkey patch may be used:

```ruby
ActionView::Helpers::JavaScriptHelper::JS_ESCAPE_MAP.merge!(
  {
    "`" => "\\`",
    "$" => "\\$"
  }
)

module ActionView::Helpers::JavaScriptHelper
  alias :old_ej :escape_javascript
  alias :old_j :j

  def escape_javascript(javascript)
    javascript = javascript.to_s
    if javascript.empty?
      result = ""
    else
      result = javascript.gsub(/(\\|<\/|\r\n|\342\200\250|\342\200\251|[\n\r"']|[`]|[$])/u, JS_ESCAPE_MAP)
    end
    javascript.html_safe? ? result.html_safe : result
  end

  alias :j :escape_javascript
end
```

### Patches

To aid users who aren't able to upgrade immediately we have provided patches for
the two supported release series. They are in git-am format and consist of a
single changeset.

* [5-2-js-helper-xss.patch](https://gist.github.com/tenderlove/c042ff49f0347c37e99183a6502accc6#file-5-2-js-helper-xss-patch) - Patch for 5.2 series
* [6-0-js-helper-xss.patch](https://gist.github.com/tenderlove/c042ff49f0347c37e99183a6502accc6#file-6-0-js-helper-xss-patch) - Patch for 6.0 series

Please note that only the 5.2 and 6.0 series are supported at present. Users
of earlier unsupported releases are advised to upgrade as soon as possible as we
cannot guarantee the continued availability of security fixes for unsupported
releases.

### Credits

Thanks to Jesse Campos from Chef Secure

## References
- https://github.com/rails/rails/security/advisories/GHSA-65cv-r6x7-79hv
- https://nvd.nist.gov/vuln/detail/CVE-2020-5267
- https://github.com/rails/rails/commit/033a738817abd6e446e1b320cb7d1a5c15224e9a
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionview/CVE-2020-5267.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/55reWMM_Pg8
- https://lists.debian.org/debian-lts-announce/2020/03/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XJ7NUWXAEVRQCROIIBV4C6WXO6IR3KSB
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00019.html
- http://www.openwall.com/lists/oss-security/2020/03/19/1
