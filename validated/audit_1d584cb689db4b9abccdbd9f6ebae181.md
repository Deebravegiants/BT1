### Title
Webhook `shop-domain` header is trusted for tenant routing but not covered by the HMAC signature, enabling cross-tenant webhook confusion - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) used for dispatching a webhook to the app's handler exclusively from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Registry.process` validates covers only the raw request body. This breaks the identity binding `shop_used_for_handler_dispatch == shop_covered_by_hmac`: the byte range that is verified (the body) is disjoint from the byte range that is acted on for tenant attribution (the header).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cross-check against the HMAC-signed payload: [2](#0-1) [3](#0-2) 

`Registry.process` only verifies the HMAC via `Utils::HmacValidator.validate(request)` (which calls `to_signable_string`, i.e. body-only) and then immediately forwards `request.shop` (the unauthenticated header) into `WebhookMetadata`, which is handed to the app's `WebhookHandler#handle`: [4](#0-3) [5](#0-4) [6](#0-5) 

Because the HMAC secret (`Context.api_secret_key`) is the same `client_secret` for the app across all installed shops, and the signature is computed only over the body, any two webhook deliveries with identical body content produce identical valid HMAC signatures regardless of which shop they originated from. An actor who controls their own (unprivileged) shop installation can capture a genuinely-signed webhook for content they control, then replay the exact same body + HMAC to the app's webhook endpoint while substituting the `shop-domain` header for a different (victim) shop. `Registry.process` will pass HMAC validation (since the body/HMAC pair is valid for the secret) and hand the handler a `WebhookMetadata` whose `shop` field is the attacker-chosen victim shop, even though the payload was never actually signed for or sent by that shop.

This is the direct analog of the reported bug class: a field that is acted upon (here, the tenant/shop attribution used to route and process the webhook payload) is not covered by the integrity check (the HMAC), so the equality `shop_verified == shop_acted_on` silently fails.

### Impact Explanation
This is a cross-tenant confusion vector (High/Critical per the given severity classes: "cross-tenant access"). A host application that uses `WebhookMetadata#shop` (as documented/intended by this gem) to select which merchant's records to update, or to key into per-shop session/data stores, can be tricked into applying legitimately-signed webhook data under the wrong shop's identity, or into processing attacker-crafted content as if it were authoritative data belonging to a shop the attacker doesn't control. Depending on the topic (e.g. `customers/redact`, `shop/redact`, `orders/*`), this can lead to unauthorized data mutation/deletion attributed to another tenant.

### Likelihood Explanation
Exploitability requires the attacker to be able to obtain at least one genuinely-signed webhook body/HMAC pair for the app (trivially achievable by installing the app on their own store, an unprivileged action) and to be able to send arbitrary HTTP headers to the app's public webhook endpoint (also unprivileged, internet-reachable by design since Shopify delivers webhooks over the open internet). No access token, `api_secret_key`, or privileged account is required — only the app's public webhook URL and a captured/generated body+HMAC pair.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`/`webhook_id`) into the signable string used for HMAC verification, or independently verify that the shop domain asserted in the header matches a value cryptographically tied to the payload (e.g., include shop domain in the HMAC computation as Shopify's webhook signature effectively expects consumers to validate against the exact raw body delivered to that shop's registered endpoint, and additionally correlate the header shop against records of webhooks actually registered/expected for that shop). At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (unprivileged, self-service via Shopify).
2. Attacker triggers a webhook topic they control (e.g. `orders/create`) and captures the raw body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` that Shopify computed using the app's `client_secret`.
3. Attacker POSTs to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (header presence checked, not content), `Utils::HmacValidator.validate` succeeds because `to_signable_string` is body-only: [7](#0-6) 
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))`, causing the app to process attacker-controlled content under the victim shop's identity. [8](#0-7)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
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
