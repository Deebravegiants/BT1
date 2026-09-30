# [M] Ruby SAML DOS vulnerability with large SAML response

## Summary
Severity: Medium
Advisory: GHSA-rrqh-93c8-j966
CVE: CVE-2025-54572
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-rrqh-93c8-j966
Type: github-advisory

## Affected
- RubyGems: `ruby-saml` — affected >=0 <1.18.1

## Details
### Summary
A denial-of-service vulnerability exists in ruby-saml even with the message_max_bytesize setting configured. The vulnerability occurs because the SAML response is validated for Base64 format prior to checking the message size, leading to potential resource exhaustion.

### Details
`ruby-saml` includes a `message_max_bytesize` setting intended to prevent DOS attacks and decompression bombs. However, this protection is ineffective in some cases due to the order of operations in the code:

https://github.com/SAML-Toolkits/ruby-saml/blob/fbbedc978300deb9355a8e505849666974ef2e67/lib/onelogin/ruby-saml/saml_message.rb

```ruby
      def decode_raw_saml(saml, settings = nil)
        return saml unless base64_encoded?(saml) # <--- Issue here. Should be moved after next code block.

        settings = OneLogin::RubySaml::Settings.new if settings.nil?
        if saml.bytesize > settings.message_max_bytesize
          raise ValidationError.new("Encoded SAML Message exceeds " + settings.message_max_bytesize.to_s + " bytes, so was rejected")
        end

        decoded = decode(saml)
        ...
      end
```

The vulnerability is in the execution order. Prior to checking bytesize the `base64_encoded?` function performs regex matching on the entire input string:

```ruby
!!string.gsub(/[\r\n]|\\r|\\n|\s/, "").match(BASE64_FORMAT)
```

### Impact
_What kind of vulnerability is it? Who is impacted?_

When successfully exploited, this vulnerability can lead to:

- Excessive memory consumption
- High CPU utilization
- Application slowdown or unresponsiveness
- Complete application crash in severe cases
- Potential denial of service for legitimate users

All applications using `ruby-saml` with SAML configured and enabled are vulnerable.

### Potential Solution

Reorder the validation steps to ensure max bytesize is checked first

```ruby
def decode_raw_saml(saml, settings = nil)
  settings = OneLogin::RubySaml::Settings.new if settings.nil?

  if saml.bytesize > settings.message_max_bytesize
    raise ValidationError.new("Encoded SAML Message exceeds " + settings.message_max_bytesize.to_s + " bytes, so was rejected")
  end
  
  return saml unless base64_encoded?(saml)
  decoded = decode(saml)
  ...
end
```

## References
- https://github.com/SAML-Toolkits/ruby-saml/security/advisories/GHSA-rrqh-93c8-j966
- https://nvd.nist.gov/vuln/detail/CVE-2025-54572
- https://github.com/SAML-Toolkits/ruby-saml/pull/770
- https://github.com/SAML-Toolkits/ruby-saml/commit/38ef5dd1ce17514e202431f569c4f5633e6c2709
- https://github.com/SAML-Toolkits/ruby-saml
- https://github.com/SAML-Toolkits/ruby-saml/releases/tag/v1.18.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-saml/CVE-2025-54572.yml
- https://lists.debian.org/debian-lts-announce/2025/09/msg00001.html
