### Title
Webhook `shop-domain` header is trusted for tenant attribution without HMAC coverage - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which signs only `request.to_signable_string` (the raw body). The `shop` value used to attribute the webhook to a tenant is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `#shop` is derived independently from the `shopify-shop-domain` header [2](#0-1) . `Registry.process` validates the request purely against this signable string via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` (and `request.topic`) to dispatch the webhook and construct `WebhookMetadata` used by the app's handler [3](#0-2) . `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` and compares it against the `hmac` header only [4](#0-3) ; the shop header plays no role in that computation.

This matches the requested bug class exactly: a field ("shop") acted upon by the app (tenant attribution/routing) is not covered by the binding, i.e., `HMAC(raw_body) == header` is verified, but `shop_used_by_handler == shop_that_was_actually_signed` is never checked. Because the raw body is attacker-observable (bodies for a given topic/shape are effectively public/predictable JSON), and the shop-domain header sits outside the signed material, an attacker who can replay or forward a legitimately-signed webhook payload (e.g., a webhook originally sent for their own shop, or one intercepted via a compromised proxy/CDN layer in front of the app) can present it with an arbitrary `shopify-shop-domain` header value while keeping the original valid HMAC and body — the gem's own validation logic has no mechanism to reject this.

### Impact Explanation
This breaks the tenant-attribution boundary: a webhook authenticated by a valid HMAC computed over its own shop's payload can be re-labeled to any other shop, since `shop` is not part of what is signed. In a multi-tenant app that trusts `WebhookMetadata#shop` (populated straight from `request.shop`) to select which merchant's records to mutate, this enables cross-tenant data corruption/access purely by manipulating an HTTP header that carries no cryptographic binding to the signed body. This lands squarely in the "cross-tenant access" Critical impact category defined by the scope rules, since the identity binding `signed_shop == asserted_shop` is never enforced by the gem.

### Likelihood Explanation
Exploitation does not require the app's `client_secret` or an access token — the attacker only needs one legitimately-signed webhook body (own shop's traffic is sufficient, since HMAC secret is shared per app, not per-shop) and the ability to alter/forge the delivery's `shopify-shop-domain` header when it reaches the app's webhook endpoint (e.g., via a malicious/compromised intermediary, a custom webhook forwarding pipeline, or any endpoint that accepts raw headers not authenticated end-to-end by Shopify's TLS delivery, which many self-hosted receivers replicate for queuing/replay). Given the gem itself provides zero constraint tying header to signed bytes, likelihood of the binding gap being exploitable depends entirely on the host's exposure of headers to tampering, which is common in reverse-proxy / queue-based webhook architectures.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) as part of the HMAC-verified material, or otherwise cryptographically bind the header-derived tenant identity to the signed payload before `Registry.process` trusts `request.shop`. At minimum, document that host applications must independently verify the shop domain via a source that is bound to the signature (e.g., cross-check against the shop that owns the specific `webhook_id`/subscription) rather than trusting the raw header value for tenant dispatch.

### Proof of Concept
1. Attacker's own shop receives a legitimate webhook: body `B`, headers `shopify-hmac-sha256: H(secret, B)`, `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: orders/create`.
2. Attacker intercepts/replays this exact `(B, H)` pair to the app's webhook endpoint but modifies the `shopify-shop-domain` header to `victim-shop.myshopify.com` (feasible wherever the receiving stack does not itself cryptographically bind headers, e.g. custom proxies/queues sitting in front of the Rack app).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares to `H` — this passes because `B` and `H` are unchanged. [5](#0-4) 
4. `request.shop` returns the attacker-supplied `victim-shop.myshopify.com` [2](#0-1) , and `WebhookMetadata.new(..., shop: request.shop, ...)` is handed to the app's handler as if it were an authentic webhook for `victim-shop` [6](#0-5) .
5. The handler processes attacker-controlled body content while believing it originates from `victim-shop`, achieving cross-tenant confusion using only the attacker's own valid signature.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
