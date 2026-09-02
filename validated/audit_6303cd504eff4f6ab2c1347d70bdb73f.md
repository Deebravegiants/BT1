### Title
Webhook `shop` (and `topic`) identity is trusted from unauthenticated headers while the HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
This is the same bug class as the reported `fee_amount` flaw: a value that is *acted upon* is not actually *covered by the check that is supposed to authenticate it*. In the fee bug, `fees` was used to gate a return value without being validated against the correct sentinel. Here, `ShopifyAPI::Webhooks::Request#shop` and `#topic` are used to route and authorize webhook handling, but the cryptographic check (`Utils::HmacValidator.validate`) only verifies the raw JSON body, not these header-derived identity fields.

### Finding Description
`ShopifyAPI::Webhooks::Request` reads `shop`, `topic`, `api_version`, and `webhook_id` straight from HTTP headers with no cryptographic binding: [1](#0-0) 

Its `to_signable_string` — the only material the HMAC is computed over — is exclusively the raw body: [2](#0-1) 

`Registry.process` verifies only this body-derived HMAC, then trusts `request.shop` and `request.topic` unconditionally to select the handler and to build the `WebhookMetadata` passed to app code: [3](#0-2) 

Contrast this with the OAuth callback's `AuthQuery`, where `shop` **is** included inside `to_signable_string` and therefore is actually bound by the HMAC: [4](#0-3) 

The identity equality that should hold is:
`shop_authenticated_by_hmac == shop_used_by_handler`

But in the webhook path this becomes:
`shop_in_signable_string (∅, not present) != shop_used_by_handler (request.shop, from header)`

Because the header value is never included in the signed material, `OpenSSL.secure_compare(computed_signature, received_signature)` in `HmacValidator#validate_signature` only proves "this body was HMAC'd with our secret" — it proves nothing about which shop or topic the message is "for": [5](#0-4) 

### Impact Explanation
An unprivileged internet user who can obtain (or replay) any one legitimately-signed webhook body+HMAC pair for the app (e.g., a webhook payload that is not secret, or one previously delivered to the app's endpoint) can resubmit that exact `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while freely setting the `x-shopify-shop-domain` and `x-shopify-topic` headers to any value. `HmacValidator.validate` will still return `true` because it only checks the body bytes against the secret, and `Registry.process` will then dispatch to the handler with an attacker-chosen `shop` in `WebhookMetadata`. If the host application uses this `shop` value to look up per-tenant state (session, DB scoping, etc.) — which is the documented/expected usage of this field — this becomes a cross-tenant confusion: data or actions intended for shop A get attributed to shop B, or a webhook is processed under a forged topic. This matches the "cross-tenant access" criterion for a Critical-impact finding.

### Likelihood Explanation
This requires the attacker to have access to at least one valid `(raw_body, hmac)` pair produced by Shopify for the target app (webhook bodies are often not treated as secret, and topic/shop headers are the *only* thing separating tenants/messages once a body is captured). No `api_secret_key` or access token is needed — this is purely a replay of the HMAC across an unauthenticated header, fitting squarely in the "field acted on but not covered by the HMAC" analog class named in the rules.

### Recommendation
Include `shop`, `topic`, and (if relevant) `webhook_id`/`api_version` inside the signed material verified by `HmacValidator`, or otherwise cryptographically bind the header-derived identity fields before they are used for dispatch/session lookups — mirroring how `AuthQuery#to_signable_string` binds `shop` for the OAuth callback flow.

### Proof of Concept
1. Register a webhook handler for topic `orders/create` that looks up/acts on `data.shop`.
2. Capture (or otherwise obtain) any one legitimately Shopify-signed webhook delivery: `raw_body` + `x-shopify-hmac-sha256`.
3. POST that exact `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: orders/create` (any topic already registered).
4. `Utils::HmacValidator.validate` succeeds (body+secret match); `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` in `WebhookMetadata`, even though that shop never sent or received this payload — demonstrating the identity fields are unauthenticated relative to the HMAC check. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
