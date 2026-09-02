### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity headers are trusted without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `api_version`, and `webhook_id` fields — which are handed to the app's webhook handler as trusted tenant/routing identifiers — are read straight from unauthenticated HTTP headers. This breaks the intended binding `hmac == HMAC(secret, shop || topic || body)` down to `hmac == HMAC(secret, body)`, i.e. the signature never binds the claimed shop to the payload, enabling replay of a legitimately-signed webhook body under a different shop's identity.

### Finding Description
`Utils::HmacValidator.validate` verifies a request by recomputing the HMAC over `verifiable_query.to_signable_string` and comparing it to the `hmac` field: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw request body: [2](#0-1) 

But `Request#shop` (along with `topic`, `api_version`, `webhook_id`) is read directly from the incoming HTTP header, completely outside the HMAC's signed content: [3](#0-2) 

`Registry.process` calls `HmacValidator.validate(request)` — which only checks the body bytes — and then unconditionally forwards `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version`) to the app's handler as authenticated tenant/event metadata: [4](#0-3) 

The identity equality the library implicitly claims to hold is:
```
shop_used_by_handler == shop_that_the_HMAC_actually_authenticates
```
In reality, because `to_signable_string` only covers `@raw_body`, the equality that actually holds is:
```
hmac authenticates body_bytes_only
shop (and topic/webhook_id/api_version) == whatever the attacker put in the header, unverified
```//
Any webhook whose body content the attacker can obtain together with its valid `x-shopify-hmac-sha256` (e.g. from a webhook legitimately delivered to a shop the attacker controls/owns, since the app's `client_secret`/webhook secret is shared across all shops using the same app) can be replayed verbatim to the app's webhook endpoint with the `shop-domain` header rewritten to a different (victim) shop. `HmacValidator.validate` will still pass because it only checks the untouched body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This is a Critical cross-tenant access vector: an app built on this gem that uses `WebhookMetadata#shop` (as populated by `Registry.process`) to key data lookups, session retrieval, or business logic will act on/for the wrong tenant when fed a replayed, header-altered request. Because the underlying `to_signable_string` design signs body content only, an app cannot distinguish "this event genuinely happened to shop X" from "this identical body was replayed and re-labeled as shop X" using the primitives this gem provides.

### Likelihood Explanation
Exploitation requires the attacker to already possess a validly-signed webhook payload for at least one shop (trivial for an attacker who installs the target app on their own store and captures their own webhook deliveries, since app-level `client_secret` is shared across all shop installations for HMAC purposes). Rewriting the `shopify-shop-domain` header and replaying the POST to the app's public webhook endpoint requires no privileged credentials, TLS interception, or knowledge of the `client_secret`, only network access to the endpoint — this is squarely an unprivileged-internet-user attack.

### Recommendation
Include the identity fields the app relies on (at minimum `shop`) in the HMAC-signed content, or otherwise cryptographically bind them to the body, e.g. by having `to_signable_string` return a canonicalized combination of `shop`, `topic`, `webhook_id`, and `@raw_body` rather than `@raw_body` alone, and validating that combination. Alternatively, document and enforce that consuming applications must independently verify the shop domain against a known/installed-shop allowlist before trusting `WebhookMetadata#shop`, rather than deriving trust solely from `HmacValidator.validate`.

### Proof of Concept
```ruby
# Attacker owns "attacker.myshopify.com" with the same app installed.
# 1. Attacker triggers/receives a legitimate webhook, capturing:
raw_body = '{"id": 123, "note": "sensitive update"}'
valid_hmac_b64 = "<value from x-shopify-hmac-sha256 header of the captured request>"

# 2. Attacker replays the exact same body+hmac to the app's public webhook
#    endpoint, but swaps the shop-domain header to the victim shop:
headers = {
  "x-shopify-topic" => "orders/updated",
  "x-shopify-hmac-sha256" => valid_hmac_b64,      # still valid: body unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unauthenticated
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) passes (checks raw_body only, see
#    lib/shopify_api/webhooks/request.rb:35-38 and
#    lib/shopify_api/utils/hmac_validator.rb:26-31)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))
#    is invoked as if the event genuinely came from victim-shop.
```

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
