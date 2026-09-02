## Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` (and `topic`, `webhook_id`, `api_version`) from HTTP headers that are never included in the HMAC computation. `Registry.process` only validates that the raw request body matches the `hmac-sha256` header, then unconditionally trusts `request.shop`/`request.topic` when dispatching to the registered handler. This breaks the binding `shop_signed == shop_used`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read directly from HTTP headers that are not part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e., the body only) and compares it against the `hmac` field: [3](#0-2) 

`Registry.process` performs exactly this check, then forwards the caller-supplied (unauthenticated) `shop` and `topic` values straight into the handler dispatch: [4](#0-3) 

So the equality the code implicitly assumes — "the `shop` this webhook is attributed to" == "the `shop` whose HMAC secret produced this signature" — never actually holds, because `shop` is not covered by the signature at all. Any request whose body/hmac pair is valid for *some* shop (e.g., a shop the attacker legitimately controls and has installed the app on) will pass `HmacValidator.validate` regardless of what `x-shopify-shop-domain` (or `shopify-shop-domain`) header value accompanies it.

### Impact Explanation
An attacker who owns/controls one shop that has the app installed receives genuine webhook deliveries from Shopify with a valid `hmac-sha256` header computed over the body using the app's `client_secret`. Because `shop`/`topic` are not part of the signed content, the attacker can resend the exact same `raw_body` + `hmac` header to the app's public webhook endpoint while substituting the `shop-domain` (and/or `topic`) header with a different, victim tenant's domain. `Registry.process` will accept it (HMAC still validates against the body) and hand the handler a `WebhookMetadata` claiming to originate from the victim shop: [5](#0-4) 

If the host app uses `WebhookMetadata#shop` to select which tenant's records to create/update/delete (a standard and documented usage pattern per this gem's own webhook docs), this is a cross-tenant data injection: attacker-controlled webhook content gets attributed to and processed under another merchant's identity — a cross-tenant access impact.

### Likelihood Explanation
Medium-High: no secret material is required, only the ability to run a shop with the app installed (which is the normal, low-privilege path any developer/attacker can take), capture one legitimately delivered webhook, and replay it with a modified header to the app's public webhook endpoint.

### Recommendation
Include `shop` (and ideally `topic`) in the HMAC-covered content, or otherwise cryptographically bind the header-derived tenant identity to the verified payload before it is passed to `WebhookMetadata`/handlers, e.g., by deriving `shop` from a value that is itself signed (as Shopify's `X-Shopify-Shop-Domain` is not part of the signature by design, the app should re-verify tenant identity via an authenticated channel — e.g., look up the webhook by `webhook_id` against Shopify's API — rather than trusting the header outright).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and registers for a webhook topic (e.g., `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `client_secret`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the identical body `B` and header `H` to the same endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [6](#0-5) 
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` and processes attacker-supplied content as if it came from `victim-shop.myshopify.com`.

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
