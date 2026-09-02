This confirms the root cause: the webhook HMAC only covers `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers and passed downstream unbound to the signature.### Title
Webhook `shop-domain`, `topic`, and `webhook_id` headers are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw body only, but the `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` and forwarded to the app's webhook handler are read straight from unauthenticated HTTP headers. This breaks the identity binding `shop (verified by HMAC) == shop (acted upon by handler)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are pulled directly from the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers with no cryptographic binding to those values: [2](#0-1) 

`Registry.process` validates the HMAC (which only authenticates the body bytes) and then trusts `request.shop` and `request.topic` when constructing the metadata handed to the app's handler: [3](#0-2) 

Contrast this with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` (and `host`, `code`, `state`, `timestamp`) are explicitly included in `to_signable_string` and therefore bound by the HMAC: [4](#0-3) 

This asymmetry means the webhook path validates "bytes verified" (raw body signed with the app's secret) but "bytes parsed and acted on" (shop, topic, webhook id) are disjoint — exactly the class of identity-binding break called out in the rules. An attacker who can obtain one genuine, correctly-signed webhook delivery for the shared app secret (e.g., by installing the target app on their own store and receiving a real webhook) can replay that same raw body to the app's webhook endpoint while substituting arbitrary `shopify-shop-domain` and `shopify-topic` header values. `Utils::HmacValidator.validate` will still succeed because it only recomputes the HMAC over the unchanged raw body: [5](#0-4) 

The app's handler then receives `WebhookMetadata` with an attacker-chosen `shop` and/or `topic` bound to a body that was never actually associated with that shop or topic by Shopify, enabling cross-tenant data confusion inside the host application (e.g., processing another merchant's mandatory GDPR redact topics against the attacker-chosen shop, or feeding one tenant's payload into a handler keyed for a different tenant).

### Impact Explanation
This falls under the High-impact category of "scope or expiry check bypass" style identity-binding breaks — here it is a tenant (shop) and message-type (topic) binding bypass. Any host application that uses `data.shop` from `WebhookMetadata` as the tenant key for persistence, authorization, or GDPR redaction logic is vulnerable to cross-tenant data misattribution using only a body the attacker legitimately received for their own shop.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate merchant on the same app (a normal, unprivileged install) and be able to receive one authentic webhook delivery — no `api_secret_key`, access token, or privileged access needed. Header spoofing to a self-hosted or reachable webhook endpoint is trivial since HTTP headers are attacker-controlled.

### Recommendation
Include `shop-domain`, `topic`, `webhook-id`, and `api-version` in the HMAC-signed material (mirroring how `AuthQuery#to_signable_string` binds `shop`, `host`, `code`, etc.), or otherwise cryptographically bind these header values to the signed payload so they cannot be altered independently of the signature.

### Proof of Concept
1. Install the target app on an attacker-controlled shop and capture one genuine webhook delivery, e.g. topic `orders/create` for `attacker-shop.myshopify.com`, with body `raw_body` and header `x-shopify-hmac-sha256: H`.
2. Replay the identical `raw_body` and `x-shopify-hmac-sha256: H` to the target app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or `x-shopify-topic: shop/redact`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`@raw_body` only) — validation succeeds since the body is unchanged. Reference: [3](#0-2)  and [1](#0-0) .
4. The app's registered handler for the spoofed topic executes with `shop: "victim-shop.myshopify.com"` and the attacker's own body content, despite Shopify never having sent that combination.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
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
