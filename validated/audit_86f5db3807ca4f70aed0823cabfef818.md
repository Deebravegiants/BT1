Confirmed: the `shop`, `topic`, `api_version`, and `webhook_id` headers are read from unauthenticated HTTP headers and passed straight into `WebhookMetadata` while `HmacValidator` only signs/verifies `to_signable_string`, which is `@raw_body`.### Title
Webhook shop/topic identity is not bound to the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating an HMAC over the raw request body only, then trusts the `shop-domain`, `topic`, `webhook-id` and `api-version` values taken from unauthenticated HTTP headers and hands them to the app's handler as `WebhookMetadata`. Because the HMAC never covers these header fields, the tenant identity (`shop`) that the host application acts on is not the same identity that was actually cryptographically verified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the signature exclusively over `verifiable_query.to_signable_string`, i.e. the raw body, using `Context.api_secret_key`: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, which are not part of the signed material: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately constructs `WebhookMetadata` from those unauthenticated header fields, passing it to the host app's handler: [4](#0-3) [5](#0-4) 

The identity binding broken here is: `hmac_verified(raw_body) == true` is treated as equivalent to `hmac_verified(shop, topic, webhook_id, api_version, raw_body) == true`. In reality only the body is authenticated; the shop/topic/webhook_id/api_version headers are asserted, not proven, by the sender.

This is the same bug class flagged in the reference report: a value that is used downstream (there, `_emissionRate`/`_k`/`_decayConstant` mixed up in the pricing formula; here, `shop`/`topic` used as the trust anchor for tenant identity) is substituted for a value that was never actually covered by the security check that is supposed to guarantee correctness/authenticity.

### Impact Explanation
Any party capable of delivering an HTTP POST to the app's webhook endpoint with a **valid `(raw_body, hmac)` pair for any shop** (e.g., the attacker's own Shopify store, which legitimately receives real, correctly-signed webhooks from Shopify for its own installation) can replay that exact body/signature while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` will still pass because it only checks the body against the secret, and the gem will hand the handler `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled data>, ...)`.

If the host application uses `data.shop` (as the gem's own documentation instructs: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) to look up a merchant session/access token, update tenant-scoped records, or route processing, this enables cross-tenant data injection/corruption — an attacker forges "webhook events" that appear to originate from and be applied to a shop they do not control, using only their own legitimate webhook credentials as raw material. This matches the "cross-tenant access" Critical-impact category defined in scope.

### Likelihood Explanation
Any developer/merchant who installs the app on their own store (an "unprivileged internet user" relative to other tenants) automatically receives correctly-HMAC'd webhooks from Shopify for their own shop, satisfying the only precondition (a valid `raw_body`+`hmac` pair) without needing `api_secret_key`, an access token, or any privileged access. They only need network reachability to the target app's public webhook URL, which is inherently public by design. The gem provides no header-binding, timestamp, or shop-consistency check to prevent this, and its own documentation encourages using `data.shop` as an authoritative tenant identifier.

### Recommendation
Extend the signable string / HMAC verification to include the identity-relevant headers (at minimum `shop`, and ideally `topic`, `webhook_id`, `api_version`) rather than the raw body alone, or otherwise cryptographically bind them (e.g., by validating that the `shop` header matches an expected/allow-listed shop before dispatch). Document explicitly that only `raw_body` is currently covered by the HMAC, so consuming applications are warned not to trust `data.shop`/`data.topic` for tenant-sensitive decisions without additional verification (such as cross-checking against a known list of installed shops).

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker replays a POST to the target app's public webhook endpoint with:
   - body: `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still a valid signature for `B`)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (spoofed)
   - `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version` (optionally spoofed too)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [6](#0-5) .
4. The registered handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <parsed B>, ...)`, and any downstream logic keyed on `data.shop` now operates as if this attacker-controlled event genuinely belongs to `victim-shop`.

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
