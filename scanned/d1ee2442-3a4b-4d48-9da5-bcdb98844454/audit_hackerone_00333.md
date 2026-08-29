# [H] RCE which may occur due to `ActiveSupport::MessageVerifier` or `ActiveSupport::MessageEncryptor` (especially Active storage)

## Summary
Severity: High
Program: Ruby on Rails
Weakness: Command Injection - Generic
Reporter: ooooooo_q
State: resolved
Disclosed: 2019-03-13T19:41:52.199Z
CVE: CVE-2019-5420
Source: https://hackerone.com/reports/473888

## Details
Since `ActiveSupport::MessageVerifier` and `ActiveSupport::MessageEncryptor` use Marshal as the default serializer, I confirmed that RCE is possible by object injection.


```ruby
# https://github.com/rails/rails/blob/v5.2.2/activesupport/lib/active_support/message_verifier.rb#L110
    def initialize(secret, options = {})
      raise ArgumentError, "Secret should not be nil." unless secret
      @secret = secret
      @digest = options[:digest] || "SHA1"
      @serializer = options[:serializer] || Marshal
    end
```

```ruby
# https://github.com/rails/rails/blob/v5.2.2/activesupport/lib/active_support/message_encryptor.rb#L145
def initialize(secret, *signature_key_or_options)
  options = signature_key_or_options.extract_options!
  sign_secret = signature_key_or_options.first
  @secret = secret
  @sign_secret = sign_secret
  @cipher = options[:cipher] || self.class.default_cipher
  @digest = options[:digest] || "SHA1" unless aead_mode?
  @verifier = resolve_verifier
  @serializer = options[:serializer] || Marshal
end
```

Especially in Rails 5.2 and later, `ActiveSupport::MessageVerifier` is used to validate the URL used in Active Storage, and attacks are possible.


```ruby
# https://github.com/rails/rails/blob/v5.2.2/activestorage/lib/active_storage/engine.rb#L81
initializer "active_storage.verifier" do
  config.after_initialize do |app|
    ActiveStorage.verifier = app.message_verifier("ActiveStorage")
  end
end
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/473888_
