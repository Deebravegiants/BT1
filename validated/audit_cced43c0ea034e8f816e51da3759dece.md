### Title
Webhook `shop` and `topic` are trusted for tenant attribution without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates HMAC integrity over the raw request body only, but the `shop`, `topic`, `api_version`, and `webhook_id` fields — all of which are used downstream to identify the tenant and dispatch business logic — come from unauthenticated HTTP headers that are never included in the signed content. This breaks the identity binding `hmac_signed_bytes == bytes_acted_on`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from request headers, none of which participate in the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only proves that `to_signable_string` (i.e., the raw body) was produced/authorized by an entity holding `Context.api_secret_key`; it says nothing about which shop or topic the request is for: [3](#0-2) 

`Registry.process` then dispatches purely based on the unauthenticated `request.topic` and forwards the unauthenticated `request.shop` straight into `WebhookMetadata`, which is handed to the app's handler as the tenant identifier for the event: [4](#0-3) 

Because the app's `api_secret_key` is the same across every shop that installs the app (it's not a per-shop secret), a `(raw_body, hmac)` pair that is valid for one shop's webhook delivery is also a cryptographically valid `(raw_body, hmac)` pair when replayed with a *different* `shop-domain` and/or `topic` header. The gem's own validation logic accepts this substitution because it never binds `shop`/`topic` into `to_signable_string`.

The identity binding that should hold is:
`hmac_verified(body) == identity_acted_on(shop, topic)`
but the implementation only verifies `hmac_verified(body)` while `shop`/`topic` are taken from unauthenticated, attacker-controllable headers.

### Impact Explanation
An unprivileged user who can install the target app on any shop (their own) can trigger a legitimate webhook, capture the resulting `(raw_body, hmac)` pair, and replay it directly to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header pointing at a victim shop. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop/topic, causing the host application to act on attacker-controlled data attributed to another tenant — a cross-tenant data-integrity/access violation.

### Likelihood Explanation
Any merchant/developer able to install the app on a shop they control can obtain a valid signed webhook body/HMAC pair for arbitrary content they can influence (e.g., product/order fields they control), then replay it toward the same public endpoint with modified `shop`/`topic` headers. No access token, `client_secret`, or privileged access is required — only the ability to install the app once and send an HTTP request to the app's own public webhook route.

### Recommendation
Bind `shop` (and ideally `topic`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived tenant/topic identifiers to the signed payload (e.g., require the app to independently confirm the shop against a value embedded in the signed body, or maintain a per-shop webhook secret/allowlist) before trusting `request.shop`/`request.topic` for dispatch in `Registry.process`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook event (e.g., `orders/create`) so Shopify delivers `raw_body` + `X-Shopify-Hmac-Sha256: H` to the app's public webhook endpoint.
2. Capture that exact `raw_body` and `H`.
3. Send a new HTTP POST to the same public webhook endpoint with:
   - Body: the captured `raw_body` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
   - Header `X-Shopify-Topic:` unchanged or forged to another registered topic
4. `ShopifyAPI::Webhooks::Request.new` parses these headers; `HmacValidator.validate` succeeds because it only checks `raw_body` against `H` (see `lib/shopify_api/utils/hmac_validator.rb:12-31` and `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `shop: "victim.myshopify.com"`, causing the host app to process attacker-supplied data as if it originated from the victim tenant.

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
