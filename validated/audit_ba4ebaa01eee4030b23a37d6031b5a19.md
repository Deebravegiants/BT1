This confirms the vulnerability path. The `Webhooks::Request` class's `to_signable_string` (used for HMAC verification) only covers `@raw_body`, while `shop`, `topic`, and `webhook_id` are all read directly from unauthenticated HTTP headers and passed downstream to the handler unverified.This confirms the finding: `Registry.process` at [1](#0-0)  validates the HMAC over `request` but then passes `request.shop`, `request.topic`, and `request.webhook_id` — all read directly from unauthenticated headers via `shopify_header` at [2](#0-1)  — into `WebhookMetadata` unchanged, while `to_signable_string` only covers `@raw_body` at [3](#0-2) .

### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/registry.rb, lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying `Utils::HmacValidator.validate(request)`, which computes the signature over `to_signable_string`, defined as just the raw HTTP body. The `shop`, `topic`, and `webhook_id` fields — which the handler uses to attribute the payload to a specific merchant/tenant — are read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) and are never part of the signed content. The equality the code implicitly assumes is: `hmac_verified(raw_body)` == `authenticated(shop)`. Those are not the same thing: the HMAC only binds the *body bytes*, not the *shop* the body is attributed to.

### Finding Description
`ShopifyAPI::Auth::Oauth::AuthQuery#to_signable_string` deliberately includes `shop` in the signed payload [4](#0-3) , so the OAuth callback binds `shop` to the HMAC. `Webhooks::Request`, however, does not follow this pattern: `to_signable_string` returns only `@raw_body` [3](#0-2) , while `shop`, `topic`, and `webhook_id` are pulled from headers via `shopify_header` [2](#0-1)  with no cryptographic binding to those values at all.

Shopify signs webhooks using the app's `client_secret`, which is the same secret for *every* shop that installs the app — it is not shop-specific. `HmacValidator.validate_signature` recomputes the HMAC purely from `to_signable_string` (the raw body) and the app secret [5](#0-4) . Consequently, a valid signature only proves "this body byte-stream was signed by our app's secret at some point for some shop" — it proves nothing about which shop the body belongs to.

`Registry.process` treats HMAC validity as sufficient authentication and then trusts the unauthenticated `request.shop` header to build `WebhookMetadata`, which is handed to the host application's handler: [1](#0-0) .

### Impact Explanation
An unprivileged merchant who has legitimately installed the app on their own shop receives genuine, correctly-HMAC-signed webhooks from Shopify for events on their own shop. Because the signature covers only the raw body and not the shop, that attacker can replay the exact same raw body + valid `hmac-sha256` header to the app's webhook endpoint while substituting a victim shop's domain in the `shopify-shop-domain` header (and/or a different `webhook-id`/`topic`). `HmacValidator.validate` still returns `true` since it never inspects those headers, so `Registry.process` invokes the handler with `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop. This is a cross-tenant identity confusion at the library layer: the gem hands the host application data that is falsely attributed to another tenant, despite passing "HMAC validation." Depending on the handler's logic (e.g., data deletion/redaction handlers such as the mandatory `customers/redact`, `shop/redact` topics, or any handler that mutates per-shop stored data keyed by `request.shop`), this can cause cross-tenant data corruption or spurious redaction/deletion actions against a shop the attacker does not own.

### Likelihood Explanation
Any user who can install the app on a shop they control (a normal, unprivileged action) can capture their own valid webhook traffic and replay it against the same publicly reachable webhook endpoint with a modified `shop-domain` header — no access to the `client_secret`, tokens, or any privileged capability is required beyond owning one shop install.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-covered signable content, or otherwise cryptographically tie the header-derived attribution fields to the verified payload before constructing `WebhookMetadata`, mirroring how `Oauth::AuthQuery#to_signable_string` includes `shop` in its signed string.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook topic the app registers (e.g. `orders/create`).
2. Capture the resulting HTTP POST: raw body `B`, and header `shopify-hmac-sha256: H` (valid signature of `B` under the app's shared secret), `shopify-topic: orders/create`.
3. Replay the POST to the same app webhook endpoint, keeping body `B` and header `shopify-hmac-sha256: H` unchanged, but replacing `shopify-shop-domain: attacker.myshopify.com` with `shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` at [6](#0-5)  returns `true` because it only checks `B` against `H`.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host application to process attacker-controlled data as if it came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L189-199)
```ruby
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

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
