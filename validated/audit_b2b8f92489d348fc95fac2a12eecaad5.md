### Title
Unvalidated `host` parameter in `ShopifyAPI::Auth.embedded_app_url` enables open redirect / forced navigation outside the authenticated shop domain - (File: lib/shopify_api/auth.rb)

### Summary
`ShopifyAPI::Auth.embedded_app_url` builds the URL that the app uses to send the merchant's top-level browser window back into Shopify Admin after OAuth/token-exchange completes. It Base64-decodes the `host` parameter and interpolates it directly into a URL with no validation that the decoded value is actually a Shopify admin host for the authenticated shop.

### Finding Description
`lib/shopify_api/auth.rb:11-23`:
```ruby
def embedded_app_url(host)
  ...
  decoded_host = Base64.decode64(host)
  "https://#{decoded_host}/apps/#{Context.api_key}"
end
``` [1](#0-0) 

The `host` parameter documented and used by this gem is the App Bridge `host` query-string value, which is attacker-influenceable in the sense that it is *not* covered by the OAuth callback HMAC (that only signs `code`, `host` used there is only checked as part of `AuthQuery#to_signable_string` during the authorization-code callback flow) and is not part of the session-token JWT signed by Shopify either. When `embedded_app_url` is invoked outside of a verified OAuth callback (e.g., on any embedded page load, as the gem's own docs describe for constructing "the host app URL for an embedded app, allowing for safer redirect to app inside appropriate shop admin", `CHANGELOG.md:197`), the method performs zero validation that the decoded value:
- ends with a legitimate `myshopify.com` / configured shop domain, or
- corresponds to the shop bound to the currently authenticated session. [2](#0-1) 

This breaks the identity binding "the shop that completed authentication == the host that receives the resulting navigation/redirect." An unprivileged actor who can influence the `host` query parameter passed to `embedded_app_url` (e.g., via a crafted install/launch link sent to a merchant) can cause the returned URL to point to an attacker-controlled domain instead of the shop's actual `admin.shopify.com`/`myshopify.com` admin page.

### Impact Explanation
`embedded_app_url` is explicitly intended by this gem to redirect the merchant's top-level window "inside the appropriate shop admin" after auth completes. Because the `host` value is not validated to be a genuine Shopify admin domain, an attacker can force the app to redirect the browser to an attacker-chosen domain at the exact point OAuth/token exchange finishes. This matches the High-impact category of "forced OAuth completion" — the merchant's browser is redirected off-platform after granting authorization, which can be leveraged for phishing pages that mimic the Shopify install-complete screen to harvest merchant credentials or trick the merchant into further actions, undermining the trust boundary the OAuth flow is meant to establish.

### Likelihood Explanation
Any unprivileged party who can get a merchant to open an app link with a crafted `host` query parameter (a normal, non-privileged action — no access token, secret, or elevated account needed) can trigger this. The gem provides no built-in safeguard, so any host application that follows the documented usage of `embedded_app_url` inherits the flaw directly from the gem's implementation.

### Recommendation
Validate the decoded `host` value against an allow-list pattern (e.g., must match `^[a-z0-9-]+\.myshopify\.com(/admin)?$` or the Shopify-managed admin domain pattern, and/or must equal the host associated with the currently authenticated session) before using it to construct any redirect URL. Reject or ignore malformed/unexpected hosts instead of blindly interpolating them.

### Proof of Concept
```ruby
# Attacker crafts a link to the merchant containing a malicious host param:
malicious_host = Base64.strict_encode64("attacker-phish.example.com")
# e.g. https://victim-app.example.com/some_embedded_entry?host=#{malicious_host}

# Inside the app, following documented usage:
url = ShopifyAPI::Auth.embedded_app_url(malicious_host)
# => "https://attacker-phish.example.com/apps/<api_key>"
# The gem returns a URL outside any Shopify domain with no validation,
# and the host app is expected to navigate top-level window to this URL.
``` [3](#0-2)

### Citations

**File:** lib/shopify_api/auth.rb (L11-23)
```ruby
      sig { params(host: T.nilable(String)).returns(String) }
      def embedded_app_url(host)
        unless Context.setup?
          raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
        end

        unless host
          raise Errors::MissingRequiredArgumentError, "host argument is required"
        end

        decoded_host = Base64.decode64(host)
        "https://#{decoded_host}/apps/#{Context.api_key}"
      end
```

**File:** CHANGELOG.md (L195-199)
```markdown
## Version 11.1.0

- [#1002](https://github.com/Shopify/shopify-api-ruby/pull/1002) Add new method to construct the host app URL for an embedded app, allowing for safer redirect to app inside appropriate shop admin
- [#1004](https://github.com/Shopify/shopify-api-ruby/pull/1004) Support full URL and scheme-less URL when registering HTTP webhooks

```

**File:** test/auth_test.rb (L14-19)
```ruby
    def test_valid_host
      assert_equal(
        ShopifyAPI::Auth.embedded_app_url(@encoded_host),
        "https://#{@host}/apps/#{ShopifyAPI::Context.api_key}",
      )
    end
```
