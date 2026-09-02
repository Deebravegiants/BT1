### Title
Webhook shop identity spoofing via headers not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, while the `shop`, `topic`, and `webhook_id` values that `ShopifyAPI::Webhooks::Registry.process` uses to route and tag the webhook to a specific tenant are read from HTTP headers that are excluded from that signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` decodes the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header for comparison: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it with `OpenSSL.secure_compare` against the `hmac` value, i.e. it authenticates `raw_body` and nothing else: [3](#0-2) 

However, `Registry.process` treats a valid HMAC as proof the entire request is authentic and then hands the unauthenticated `shop`, `topic`, and `webhook_id` headers straight to the handler as the tenant/routing identity: [4](#0-3) 
and those accessors simply read the corresponding headers without any cross-check against the signed body: [5](#0-4) [6](#0-5) 

The equality that the gem implicitly relies on is: `bytes_verified_by_hmac == bytes_the_handler_trusts_for_tenant_identity`. In reality: `bytes_verified_by_hmac == raw_body` while `bytes_the_handler_trusts_for_tenant_identity == raw_body ∪ {shop-domain header, topic header, webhook-id header}`. The header set is a strict superset of what is HMAC-covered, so the `shop` (tenant) binding is broken — any request with a *valid* `(raw_body, hmac)` pair can carry an arbitrary, attacker-chosen `shop-domain` header and still pass `Utils::HmacValidator.validate`.

### Impact Explanation
An unprivileged internet user who has legitimately received one authentic webhook delivery for their own shop (a normal, unprivileged tenant of the same app) obtains a valid `(raw_body, hmac)` pair signed with the app's `api_secret_key`. Because the signature never binds `shop-domain`, that same body+hmac pair can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to point at a different (victim) shop. `Registry.process` will pass HMAC validation and invoke the registered handler with `WebhookMetadata.new(... shop: request.shop ...)` carrying the attacker-chosen shop value, causing the host application to process/attribute data under the wrong tenant — a cross-tenant identity confusion inside a security primitive this gem exposes as "verified." This matches the High-impact class of a check that answers permissively across a tenant boundary.

### Likelihood Explanation
Likelihood is moderate to low: the attacker needs at least one genuine (raw_body, hmac) pair, which any shop owner installing the app can obtain for themselves by triggering a webhook (e.g. via a normal store action) and capturing the delivery. No possession of `api_secret_key` or access tokens is required, and no TLS interception is needed — only control over the raw HTTP request sent to the app's public webhook endpoint, which is exactly the "unprivileged internet user" capability in scope.

### Recommendation
Bind the tenant-identifying headers into the signed material, or otherwise validate `shop` against an independent trust anchor before use: include `shop-domain`, `topic`, and `webhook_id` in `to_signable_string` (mirroring Shopify's actual webhook contract where the shop domain is only trustworthy in combination with the signed body context), or require the caller to supply/confirm the expected shop out-of-band (e.g., from the route/session) rather than trusting the header value returned by `Request#shop`.

### Proof of Concept
1. Attacker owns/controls Shop A, a legitimate install of the target app.
2. Attacker triggers any webhook topic they've subscribed the app to (e.g. `orders/create`) and captures the raw HTTP request Shopify sends, including `raw_body` and `x-shopify-hmac-sha256`.
3. Attacker resends this exact `raw_body` and `hmac` header to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with Shop B's domain (a victim shop also installed on the same app).
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` is constructed; `Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the HMAC. [7](#0-6) 
5. `Registry.process` invokes the handler with `shop: request.shop` equal to Shop B, even though the payload actually originated from and describes Shop A's data — the app now processes Shop A's webhook payload as if it belonged to Shop B.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/request.rb (L30-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
