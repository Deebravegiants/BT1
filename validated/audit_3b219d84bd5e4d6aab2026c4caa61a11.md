### Title
`Webhooks::Request#shop` is read from an unsigned header while HMAC only covers `@raw_body`, allowing shop-domain spoofing on a validly-signed webhook payload - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  while `#shop` is derived from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the signed bytes [2](#0-1) . `Registry.process` trusts `request.shop` after only validating the HMAC over the body, and forwards it unchecked to the host app's `WebhookHandler` [3](#0-2) .

### Finding Description
The broken binding is: `HmacValidator.validate(request) == true` should imply `request.shop` is the shop that actually produced `request.parsed_body`. In reality `HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header [4](#0-3) , and `to_signable_string` is `@raw_body` only [1](#0-0) . The `shop` value read in `#shop` (`shopify_header("shop-domain")`) is sourced purely from attacker-controlled `@headers`, which are never mixed into the signed content [2](#0-1) [5](#0-4) .

`Registry.process` calls `Utils::HmacValidator.validate(request)` and, once it passes, constructs `WebhookMetadata.new(topic: ..., shop: request.shop, body: request.parsed_body, ...)` and hands it to the app's `handler.handle` [3](#0-2) . There is no cross-check that `request.shop` corresponds to anything inside `request.parsed_body` or `@raw_body`.

Exploit flow: the client_secret (`Context.api_secret_key`) used to sign webhooks is the app's single client secret, shared across every shop that installs the app — it is not shop-specific. An attacker who installs the app on their own development shop can, through the shop's normal Admin API access (webhook subscriptions can be created for a merchant's own shop, independent of the app's own registration), obtain a genuinely Shopify-signed `(raw_body, hmac)` pair by pointing a webhook subscription at a server they control. They then replay that identical `raw_body` and `X-Shopify-Hmac-Sha256` value directly to the target app's real webhook endpoint, but substitute `X-Shopify-Shop-Domain: victim.myshopify.com`. Because `to_signable_string` never includes the shop header, `HmacValidator.validate` still returns `true`, and `Registry.process` dispatches the attacker's own body to the handler labeled as `victim.myshopify.com`.

No existing guard closes this gap: `ShopValidator.sanitize!` is only used in the OAuth flow, not in the webhook path; `HmacValidator` checks only the body bytes; there is no comparison in `Request` or `Registry` between the header-derived `shop` and any signed field.

### Impact Explanation
Any host application that keys data storage, access control, or side effects (e.g., updating a database record, deleting data, triggering `shop/redact`-style logic) off `WebhookMetadata#shop`/`Webhooks::Request#shop` can be made to write or act on the wrong tenant's data using a payload the attacker fully controls (their own shop's data). This is a cross-tenant integrity/confidentiality issue: attacker-authored content gets attributed to and processed under an arbitrary victim shop domain, satisfying the "cross-tenant access" critical category. It is repeatable against any shop domain string of the attacker's choosing, for every webhook topic the attacker can create a subscription for.

### Likelihood Explanation
Preconditions: the attacker needs a working Shopify store where the target app is installed and needs enough Admin API access (through the app's granted access token, or the store's own admin UI) to create a webhook subscription that can be delivered to a server they control, so they can capture one genuine `(raw_body, hmac)` pair. No possession of `api_secret_key` and no traffic interception are required — the attacker legitimately receives a webhook addressed to their own server because they own the subscription's destination. After that they only need one HTTP POST to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header. This is low-cost and fully repeatable.

### Recommendation
Bind the shop identity to the signed payload before trusting it: either (a) reject/ignore `Request#shop` unless it is corroborated against a shop identifier already established via an authenticated session tied to that webhook subscription, or (b) require host apps to validate `request.shop` against their own installation records (e.g., confirm the shop is actually installed and that the specific webhook subscription id/topic pair is expected for that shop) before using it for any tenant-scoped read/write. At minimum, document clearly that `Webhooks::Request#shop` is unauthenticated and must not be used as a tenant key without additional verification.

### Proof of Concept
```ruby
# test/webhooks/request_shop_spoof_test.rb
require "test_helper"

class RequestShopSpoofTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret",
      host_name: "app.com", scope: "read_products", is_private: false, api_version: "2022-01")
  end

  def test_hmac_validates_regardless_of_shop_header
    attacker_body = '{"id":1,"note":"attacker-controlled"}'
    valid_hmac = Base64.encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", attacker_body)
    ).strip

    request = ShopifyAPI::Webhooks::Request.new(
      raw_body: attacker_body,
      headers: {
        "x-shopify-hmac-sha256" => valid_hmac,
        "x-shopify-shop-domain" => "victim.myshopify.com",
        "x-shopify-topic" => "products/update",
      },
    )

    assert ShopifyAPI::Utils::HmacValidator.validate(request)
    assert_equal "victim.myshopify.com", request.shop
    # binding shop == authenticated-owner-of(raw_body) is broken: shop is spoofable
    # while the HMAC over raw_body still validates.
  end
end
```
This demonstrates that `HmacValidator.validate` returns `true` while `request.shop` can be set to an arbitrary, unsigned value, confirming the divergence between the signed body and the trusted `shop` field.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L61-70)
```ruby
        @headers = headers
        @raw_body = raw_body
      end

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
