Confirmed: `to_signable_string` for `ShopifyAPI::Webhooks::Request` returns only `@raw_body`, and `hmac` is validated by `Utils::HmacValidator.validate` against that same raw-body string, while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated headers with no cryptographic binding to the HMAC.

### Title
Webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`/`webhook_id`/`api_version`) values used by `ShopifyAPI::Webhooks::Registry.process` to identify the tenant and dispatch the payload are read from HTTP headers that are excluded from that signature. This is the same class of bug as the reported `Well` issue: a value that is *acted on* (here, the tenant-identifying `shop` used to route/process the webhook) is not *covered* by the authenticity check (the HMAC), so it can be swapped out after a legitimately signed request has been captured.

### Finding Description
`Utils::HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are never mixed into the signed string: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches the request to the app's handler using the unauthenticated `request.shop` value as the tenant identifier, without any additional binding to the signed body: [4](#0-3) 

Equality that should hold but doesn't: `shop_used_for_dispatch == shop_covered_by_hmac`. In reality, `shop_used_for_dispatch` (the `shopify-shop-domain` header) is disjoint from the set of bytes protected by the HMAC (`raw_body` only).

### Impact Explanation
Because the app's `client_secret` is required to produce a valid HMAC over a given body, an unprivileged attacker cannot forge an HMAC for arbitrary content from scratch. However, any merchant who has installed the app (an unprivileged, low-trust actor from the app's perspective) legitimately receives Shopify-signed webhooks for their own shop and therefore can capture a `(raw_body, hmac)` pair that Shopify genuinely signed. Since the `shop-domain` header is *not* part of the signed bytes, that attacker can replay the exact same `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value (e.g., a victim shop). `HmacValidator.validate` will still succeed because it only checks the body, and `Registry.process` will hand the (attacker-supplied) `shop` value plus the replayed body to the app's handler as if it were an authentic event for that other tenant. Depending on how the host app uses `data.shop` (e.g., to look up the tenant's session/access token and act on their store), this is a cross-tenant confusion vector — the app can be tricked into associating one merchant's webhook payload with another merchant's identity.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to be an app-installing merchant (unprivileged relative to other tenants) who can trigger and capture a webhook for their own shop, and it requires the host application to trust `data.shop` from `WebhookHandler#handle` as an authoritative tenant identifier without independent cross-checking — which is exactly the documented/intended usage shown in this gem's own docs (`data.shop` is documented as "The shop domain of the webhook").

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` header values in the signed material checked by `HmacValidator`, or otherwise cryptographically bind them to the payload (e.g., by requiring apps to cross-verify `shop` against a known/allow-listed value and by validating the webhook against the `X-Shopify-Webhook-Id` for idempotency and replay protection) before dispatching to `WebhookHandler#handle`. At minimum, document clearly that `shop` in `WebhookMetadata` is unauthenticated header data not covered by the HMAC, so host apps aren't misled into using it as a trusted tenant key.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), receiving a legitimately Shopify-signed request with `raw_body = B` and header `x-shopify-hmac-sha256 = H` (valid HMAC of `B`).
2. Attacker sends a forged POST to the app's webhook endpoint with the same `raw_body = B` and `x-shopify-hmac-sha256 = H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against `H` via `to_signable_string` [2](#0-1)  — validation passes.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop = "victim-shop.myshopify.com"` [5](#0-4) , even though the shop header was never verified against the HMAC.

### Citations

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
