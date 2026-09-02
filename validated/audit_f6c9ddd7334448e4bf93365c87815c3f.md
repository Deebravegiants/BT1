### Title
Webhook `shopify-shop-domain` (and `topic`/`webhook-id`) headers are trusted for tenant identification but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC signature, but the HMAC is computed over the raw request body only. The `shop`, `topic`, and `webhook_id` values used to route and attribute the webhook to a specific merchant tenant come from unauthenticated HTTP headers, breaking the intended binding `hmac(secret, body) == received_hmac` implying `shop == authenticated_shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic protection: [2](#0-1) 

`Registry.process` validates only this body-based HMAC and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to build the metadata handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` confirms the signature only proves knowledge of `Context.api_secret_key` over the exact bytes returned by `to_signable_string` (the body) — it says nothing about the headers: [4](#0-3) 

The identity binding that should hold is: *the shop that receives credit/attribution for a webhook == the shop Shopify actually generated it for*. Because the signature never covers the `shop-domain` header, this binding is not enforced — any unprivileged app user who legitimately controls a shop where the app is installed (a normal merchant, no special credentials required) can capture a body+HMAC pair that Shopify legitimately sent for their own shop, then submit a request directly to the app's public webhook endpoint with an attacker-chosen `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header while keeping the original body and HMAC unchanged. `HmacValidator.validate` still returns `true` because the body hash matches, and `Registry.process` dispatches the handler with the forged `shop` value, so the app's handler processes attacker-controlled body content attributed to a victim tenant it was never sent for.

### Impact Explanation
This is a cross-tenant identity-confusion vulnerability: an unprivileged user (any merchant that installs the app once) can make the host application record, act on, or persist data under another merchant's shop identity via forged webhook headers, since the gem's own verification step does not bind `shop`/`topic`/`webhook_id` to the signature. This matches the Critical "cross-tenant access" impact category, since the tenant boundary the gem is supposed to enforce (webhook authenticity == correct shop attribution) is broken purely through request-header manipulation, requiring no `api_secret_key`, no access token, and no privileged account.

### Likelihood Explanation
Likelihood is high for any SaaS-style app built on this gem that serves multiple merchants and relies on `WebhookMetadata#shop`/`topic`/`webhook_id` for tenant routing (a documented, expected usage pattern of `Registry.process`). Obtaining a valid `(body, hmac)` pair requires nothing more than installing the app on any shop (normal, unprivileged action) and triggering an event the app subscribes to; forging the remaining headers on a direct HTTP request to the app's webhook endpoint requires no secret at all.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material verified against the HMAC, or otherwise cryptographically bind them to the body before trusting them for tenant attribution — e.g., verify the values against the shop that was actually resolved from a separately authenticated channel, or require Shopify to sign a canonical representation that includes these headers rather than the body alone.

### Proof of Concept
1. As a normal (non-privileged) developer, install the app on `attacker-shop.myshopify.com` and subscribe to a webhook topic the app handles.
2. Trigger the event so Shopify sends a legitimate webhook to the app's endpoint; capture the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (valid because `HMAC(api_secret_key, B) == H`).
3. Send a new HTTP POST directly to the app's public webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Request.new` parses these headers unauthenticated; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `H`.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
