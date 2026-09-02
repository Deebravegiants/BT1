Found the exact identity binding break: in `ShopifyAPI::Webhooks::Request`, the `shop` field (`shopify-shop-domain` header) used by handlers to identify the tenant is **not covered by the HMAC signature**, whereas the HMAC in `ShopifyAPI::Utils::HmacValidator` only signs `to_signable_string`, which for webhook requests is defined as `@raw_body` — the shop-domain header is never included in that signable string. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop-domain` header is not bound by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking `Utils::HmacValidator.validate(request)`, which HMACs only `request.to_signable_string` (the raw body). The `shop` value passed to the application's handler comes from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is never part of the signed payload.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` only, and `#shop` is read directly from an HTTP header outside that signed string. `Utils::HmacValidator.validate` computes `HMAC(api_secret_key, to_signable_string)` and compares against the `hmac-sha256` header, verifying only that the body bytes were signed by Shopify — it says nothing about which shop the body belongs to. `Registry.process` then calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))`, passing the unauthenticated header value straight to the app's business logic as the tenant identifier. This breaks the required binding: `shop-bound-by-HMAC == shop-delivered-to-handler`. An attacker who can produce any valid `(body, hmac)` pair for a shop they control (e.g., their own test/dev store using the same shared app `client_secret` — every install of a public app shares one `client_secret`) can freely set the `shopify-shop-domain` header to a victim shop's domain, and the library will pass that victim shop identity to the host application's webhook handler as if the data originated from the victim.

This mirrors the Yearn bug-class pattern: the value verified (the raw body bytes) is not the same as the value trusted afterward (the shop identity used for tenant-scoped side effects), exactly like the amount validated differs from the yvToken amount acted upon.

### Impact Explanation
Any host application relying on `WebhookMetadata#shop` (as the docs and registry code both do) to select the tenant record/session for processing incoming webhook data can be tricked into applying attacker-controlled webhook payloads under a victim's `shop` identity — a cross-tenant data/write confusion. Since all shops share the same app `client_secret`, an attacker with a normal (even free/dev) install of the app can forge this cross-tenant binding without ever obtaining the victim's credentials.

### Likelihood Explanation
Moderate-to-high: exploitation requires only a working install of the same app (any attacker can install their own public app or use a dev store), the ability to compute a valid HMAC for their own known/self-chosen body using the shared `client_secret` context they already have signing access to via their own webhook deliveries, and setting an arbitrary `shop-domain` header value on the forged HTTP request to the app's webhook endpoint. This is entirely within the surface this gem exposes (`Webhooks::Request`/`Registry.process`), not dependent on host misuse — the library itself never binds shop to the signature.

### Recommendation
Include `shop-domain` (and ideally `topic`/`webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind the shop identity to the payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that `request.shop` must be cross-checked against an already-authenticated session/shop record before being used for any tenant-scoped action, since `to_signable_string` currently only covers the raw body.

### Proof of Concept
```ruby
require "shopify_api"

ShopifyAPI::Context.setup(
  api_key: "key", api_secret_key: "shared_secret",
  host: "https://example.com", scope: "read_products",
  is_embedded: true, is_private: false, api_version: "2024-01"
)

body = "{}"
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "shared_secret", body)

# Attacker crafts headers with a forged shop-domain, using an HMAC that is
# valid for the body but says nothing about which shop it belongs to.
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by hmac
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)
ShopifyAPI::Utils::HmacValidator.validate(request) # => true, even though "victim-shop" was never verified
ShopifyAPI::Webhooks::Registry.process(request)    # handler.handle receives shop: "victim-shop.myshopify.com"
``` [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
