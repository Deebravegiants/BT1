## Title
Webhook `shop` (tenant) identity is taken from an unauthenticated HTTP header and never bound by the HMAC, allowing cross-tenant metadata spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using an HMAC computed only over the raw request body, then separately reads `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers that are not part of the signed payload. `Registry.process` validates the HMAC and, if valid, immediately trusts `request.shop` (and the other headers) to construct `WebhookMetadata` and dispatch it to the app's `WebhookHandler#handle`. Because the tenant-identifying `shop` value is never cryptographically bound to the signed body, an attacker who can influence or replay headers alongside a validly-signed body can present a body legitimately signed for one shop as if it belonged to a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed content [2](#0-1) . `Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` [3](#0-2) , so the validation only proves "the body bytes were signed by Shopify," not "the shop header matches the shop that produced this signed body."

`Registry.process` performs the HMAC check and then unconditionally trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build `WebhookMetadata`, which is handed directly to the app-defined handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) . `WebhookMetadata.shop` is a plain `String` constant with no further verification [5](#0-4) .

This breaks the intended identity binding: **shop header value == shop that authored the HMAC-signed body**. The gem enforces "HMAC(raw_body) is valid" but hands the tenant identity (`shop`) to the host application from a channel that is never covered by that HMAC. Any component in front of the app (proxy, load balancer, header-forwarding middleware, or a bug in Shopify's own forwarding infrastructure) that lets the `shop-domain` header diverge from the header used at signing time causes the app's webhook handler to process a genuinely-signed webhook body under the wrong tenant's identity — a cross-tenant data misattribution primitive entirely internal to how this gem parses and forwards trust.

### Impact Explanation
If a host application uses `WebhookMetadata.shop` (as documented/intended) to select which merchant's data store, session, or database shard the incoming, HMAC-verified payload should be applied to, an attacker able to manipulate only the `shop-domain` header (not the body, not the secret) can cause a validly-signed webhook to be attributed to and processed against a different tenant's records — i.e., cross-tenant access/write, without needing the app's `client_secret` or any credential. This satisfies the Critical impact bar: cross-tenant access caused purely by a gem-internal binding gap between the verified bytes and the trusted identity field.

### Likelihood Explanation
Exploitability depends on an attacker having a way to set/alter the `shop-domain` header independently from the signed body reaching the app process (e.g., a shared/multi-tenant ingress, a caching layer, header injection, or any request path where headers and body can be recombined). This is a realistic class of conditions in production deployments (reverse proxies, CDNs, webhook re-delivery tooling) but is not exploitable by a bare unauthenticated internet request against a correctly locked-down single endpoint with no header-mixing surface — so likelihood is moderate and environment-dependent, not universal.

### Recommendation
Bind the tenant identity to the signed payload: either require the `shop` domain to be embedded in the raw body/topic and compare it against the header value before dispatch, or extend `to_signable_string` (and Shopify's signing scheme, if it supports it) so headers like `shop-domain`, `topic`, and `webhook-id` are included in the HMAC computation. At minimum, `Registry.process` should treat `request.shop` as untrusted metadata unless it can be shown to be cryptographically consistent with the verified body, and document that host applications must not use it as a sole tenant-selection key without independent verification (e.g., cross-checking against the session's stored shop for that webhook subscription).

### Proof of Concept
1. App registers a webhook handler that calls `handler.handle(data:)` and uses `data.shop` to route the payload to the corresponding tenant record, per the documented flow in `lib/shopify_api/webhooks/registry.rb` (`process` method).
2. Attacker (or an intermediary the attacker can influence) captures a validly HMAC-signed webhook body for `shop-a.myshopify.com` and re-delivers it to the app's webhook endpoint while attaching `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `HmacValidator.validate` only recomputes the HMAC over `@raw_body` [1](#0-0)  — it succeeds because the body and secret are legitimate; the header is never included in the signature check [6](#0-5) .
4. `Registry.process` passes through, builds `WebhookMetadata` with `shop: request.shop` = `"shop-b.myshopify.com"` [4](#0-3) , and the handler processes shop-a's data under shop-b's identity.

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
