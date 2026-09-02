This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, meaning the HMAC computed by `Utils::HmacValidator.validate` in `Registry.process` never covers the `shop`, `topic`, `webhook_id`, or `api_version` values, which are all read from unauthenticated HTTP headers via `shopify_header`.This confirms `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`, lines 12-22 and 26-31) computes the signature strictly from `verifiable_query.to_signable_string`, which for `Webhooks::Request` is just the raw body — the `shop`, `topic`, and `webhook_id` header values are never part of what's cryptographically verified, yet `Registry.process` (`lib/shopify_api/webhooks/registry.rb` lines 188-200) trusts them directly to build `WebhookMetadata` passed to the app's handler.

### Title
Webhook shop/topic/webhook_id identity spoofing via HMAC that only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `ShopifyAPI::Webhooks::Registry.process` are read from unauthenticated HTTP headers. Because those identity-critical fields are not bound to the HMAC signature, a party who can obtain one valid `(body, hmac)` pair (e.g., by installing the app on their own store, a routine unprivileged action) can replay that exact body/HMAC to the app's public webhook endpoint while substituting arbitrary values for the `shop-domain`, `topic`, and `webhook-id` headers. `Utils::HmacValidator.validate` will still report the signature as valid because it never inspects those headers, and the app's handler will process the forged webhook as if it legitimately originated from — and pertains to — a different shop or topic.

### Finding Description
`Registry.process` verifies authenticity purely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

That validator computes and compares the HMAC using only `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns solely `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers that participate in no cryptographic check whatsoever: [3](#0-2) 

This breaks the intended identity binding `hmac(body) == hmac(body, shop, topic, webhook_id)`: the signature that Shopify computes for one shop/topic combination remains valid for the *same body* delivered to the app's endpoint under a completely different `shop-domain`/`topic`/`webhook-id` header set, because none of those fields are covered by the signed content. `WebhookMetadata` is then built directly from these unverified header values and handed to the app's handler as trusted data: [4](#0-3) 

### Impact Explanation
Any unprivileged actor able to run the app on a shop they control (a normal, unprivileged flow — installing a free/dev app requires no special privilege) can capture a legitimately-signed `(body, hmac)` pair for a webhook triggered on their own store, then send an HTTP POST directly to the app's public webhook endpoint with that same body/HMAC but forged `shop-domain`/`topic`/`webhook-id` headers claiming to be a different, victim shop or a more sensitive topic (e.g. `shop/redact`, `customers/data_request`, `app/uninstalled`). Because `Registry.process` trusts these headers once `HmacValidator.validate` passes, this enables cross-tenant impersonation — the handler acts on behalf of a shop that never actually sent the event, potentially triggering data deletion/redaction, state changes, or record association for the wrong tenant. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Webhook endpoints are, by design, public HTTP endpoints reachable by anyone on the internet who knows the URL (documented usage shows a bare unauthenticated Rails route accepting `request.raw_post` and `request.headers`): [5](#0-4) 
Obtaining a valid `(body, hmac)` pair requires no secret knowledge — only the ability to receive one real webhook delivery from Shopify for a shop the attacker controls (trivial for anyone who installs the app). No access token, `client_secret`, or other privileged credential is needed to mount the header-substitution replay.

### Recommendation
Bind the shop, topic, and webhook_id to the HMAC-verified content, not just the raw body. Since Shopify does not include these fields in the signed payload itself, the gem should, at minimum, document/require verifying `shop` against the app's known/installed shop list before dispatching to a handler, and treat `topic`/`webhook_id` from headers as unauthenticated hints unless corroborated by fetching the true state via an authenticated Admin API call using a securely stored access token for the claimed shop, rather than trusting header values as authoritative identity for cross-tenant-sensitive actions.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) with an empty/known body, capturing the resulting `X-Shopify-Hmac-Sha256` header value, which Shopify computed as `HMAC-SHA256(api_secret_key, raw_body)`.
2. Attacker sends `POST /callback/webhook` directly to the target app's public webhook endpoint with:
   - the same `raw_body` and `X-Shopify-Hmac-Sha256` captured in step 1,
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`,
   - `X-Shopify-Topic: shop/redact` (or any other registered topic).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, raw_body)` — identical to step 1 — and passes, even though `shop`/`topic` were changed: [6](#0-5) 
4. The registered handler for `shop/redact` is invoked with `data.shop == "victim-shop.myshopify.com"`, causing the app to perform shop-redaction (or whatever the topic's action is) against a shop the attacker never actually controls or received a real event for.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L127-136)
```markdown
```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
