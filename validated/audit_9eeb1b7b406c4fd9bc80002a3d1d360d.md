### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC signature only ever covers the raw request body. The `shop`, `topic`, `webhook-id`, and `api-version` values, all taken directly from HTTP headers, are never part of the signed data. Since every shop that installs the app receives the *same* `api_secret_key`, any shop (including a free/unprivileged dev store) can generate a validly-signed webhook body for itself and then replay that body with a forged `x-shopify-shop-domain` header claiming to be a different, victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are read straight from (attacker-controllable) headers with no cryptographic binding: [2](#0-1) 

`Registry.process` only checks the HMAC before dispatching to the handler, then forwards the *unverified* `request.shop` and `request.topic` values as the tenant/topic identity for the handler to act on: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute and compare the signature strictly over `verifiable_query.to_signable_string`, i.e. the body only: [4](#0-3) 

The binding that should hold is:
`hmac == HMAC(secret, body ‖ shop ‖ topic)` — but the gem only enforces `hmac == HMAC(secret, body)`, leaving `shop` and `topic` unauthenticated even though they are trusted and acted upon by the handler (`WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, see the same `registry.rb` lines above).

Because the `api_secret_key` is shared across every shop that has the app installed (it is the app's client secret, not a per-shop secret), a low-privilege attacker only needs to install the app on their own (free) dev store to obtain valid `(body, hmac)` pairs from real Shopify webhook deliveries. They can then replay that exact body/hmac pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) for a victim shop that also has the app installed. `HmacValidator.validate` still passes (it never looked at the header), and the handler receives `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
This breaks the tenant-isolation guarantee the HMAC check is meant to provide. A handler that uses `data.shop` to look up per-shop state, apply per-shop business logic, or write data keyed by shop (a very common pattern, and the one demonstrated in this gem's own webhook example/tests) will process attacker-supplied body content under a victim shop's identity — a cross-tenant access primitive. This matches the Critical severity class ("cross-tenant access") called out in the rules, since no privileged credential or token is required — just the ability to install the app on any shop.

### Likelihood Explanation
Likelihood is high for any consumer of this gem that follows the documented pattern of trusting `WebhookMetadata#shop`/`#topic` post-HMAC-check (as shown in the gem's own tests, e.g. `test_process_with_new_format_headers` asserting `data.shop == @shop` straight from the header). The only prerequisite is installing the app once as an unprivileged merchant to obtain a valid signed webhook body/HMAC pair, then replaying it with a modified `shop` header — no secret material or elevated access is needed.

### Recommendation
Bind the tenant-identifying fields into the signable data (e.g., include `shop`, `topic`, and `webhook_id` in the string that is HMAC-verified, or require host applications to independently verify that `data.shop` corresponds to a shop session with a currently valid access token/installation record before trusting it), rather than relying on the header value alone once the body signature checks out.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets Shopify deliver a real webhook (e.g. `orders/create`) with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker resends the same `B` and same HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` — this matches, so validation succeeds.
4. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: B, ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
