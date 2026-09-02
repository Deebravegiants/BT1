### Title
Webhook shop-tenant identity is not bound to the HMAC-verified payload, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, but the `shop` field that the handler uses to attribute the event to a tenant is taken from an HTTP header that is never included in the signed data.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that body [2](#0-1) . `Registry.process` validates the request only via `Utils::HmacValidator.validate(request)` (which checks `hmac(raw_body, secret)`), then immediately forwards `request.shop` to the handler as the trusted tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [3](#0-2) .

This breaks the intended identity binding:
`HMAC-verified(raw_body) == true` should imply `shop == the tenant that produced raw_body`, but the equality does not hold because `shop` is never part of `to_signable_string`.

An unprivileged internet user who runs the app on their own shop receives genuine webhook deliveries with a valid HMAC computed by Shopify over the body using the app's `client_secret`. Since the HMAC never covers the `shopify-shop-domain` header, that user can replay the exact same body + HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` value (a victim's shop domain). `HmacValidator.validate` will still return `true` because it only recomputes the signature over `@raw_body` [4](#0-3) , and the handler will process the event believing it originated from the victim shop, because `WebhookMetadata.shop` is populated from the unverified header [5](#0-4) .

### Impact Explanation
This is a cross-tenant identity confusion: any host application that uses `request.shop` (or the resulting `WebhookMetadata#shop`) to look up a session/shop record, trigger per-tenant side effects (e.g., mandatory `shop/redact`, `customers/redact`, `customers/data_request` handling, billing/plan updates, cache invalidation), or otherwise gate logic by shop, can be made to act on behalf of, or attribute data to, a shop the attacker does not control — despite a "verified" HMAC. This matches the Critical "cross-tenant access" impact category, since the trust boundary between tenants is defined entirely by this unauthenticated header.

### Likelihood Explanation
Exploitation requires only that the attacker installs the app on a shop they control (a normal, unprivileged action) in order to receive at least one legitimately HMAC-signed webhook body, then replay it against the app's public webhook endpoint with a modified `shopify-shop-domain` header. No access token, `client_secret`, or elevated privilege is required — this is exactly the kind of "verified bytes vs. acted-upon field" mismatch called out in the analog rules.

### Recommendation
Include the shop-identifying value in the HMAC-signed material, or otherwise cryptographically bind the `shop` header to the same authenticated context as the body (e.g., require the host application to independently re-validate that `request.shop` corresponds to a shop with an existing installation/session before trusting it), and document that `request.shop` must not be treated as verified by `HmacValidator.validate` alone.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery: raw body `B`, header `shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `client_secret`), header `shopify-shop-domain: attacker.myshopify.com`.
2. Replay the same request to the app's webhook endpoint, keeping `raw_body = B` and `shopify-hmac-sha256 = H` unchanged, but set `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely over `B` [1](#0-0)  and succeeds because `B` and `H` are unchanged.
4. The registered handler receives `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed_body)` [5](#0-4)  and processes attacker-supplied data as if it came from the victim shop.

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
