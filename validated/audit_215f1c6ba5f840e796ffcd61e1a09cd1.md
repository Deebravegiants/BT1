### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header) is read directly from unauthenticated headers and passed straight through to the webhook handler as the tenant identifier. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC of the body, then unconditionally trusts `request.shop` as the identity used to route/attribute the event. This breaks the identity binding: `shop` validated by HMAC` ≠ `shop` used as the tenant key handed to the app`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is derived purely from a header, with no cryptographic tie to the signed body: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.to_signable_string` (i.e., the body) against `verifiable_query.hmac` — it never touches `shop`: [3](#0-2) 

`Registry.process` validates only this body HMAC, then immediately forwards `request.shop` (unauthenticated) into `WebhookMetadata` for the handler to act on as the merchant/tenant identity: [4](#0-3) 

Because `shop` is never part of the signed payload, any request bearing a *valid* `(raw_body, hmac)` pair — which an attacker who legitimately controls their own installed shop can obtain (Shopify sends them real, validly-signed webhooks for their own shop) — can be replayed with the `shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still pass, because it only checks the body/secret pair, not the shop claim. The gem then hands `data.shop = <victim shop>` together with the attacker's own webhook body to the registered handler, which is exactly the pattern called out in the report: "a field acted on but not covered by the HMAC."

### Impact Explanation
This is a cross-tenant identity-binding break: the identity that was cryptographically verified (i.e., "some request signed with our shared app secret") is not the identity ("shop") that ends up driving tenant-scoped processing in the host application (session/data lookups keyed by `data.shop`). An attacker with a legitimate account (any single unprivileged shop that installed the app) can produce forged events that are processed by the app as though they originated from a different (victim) shop, e.g. triggering data mutation, deletion (`shop/redact`, `customers/redact`), or business logic tied to `data.shop` for a shop they do not control. This satisfies the "cross-tenant access" high-impact criterion because a boundary between tenants (shops) is defeated using only material available to any regular unprivileged app installer.

### Likelihood Explanation
Moderate: it requires the attacker to (a) have their own shop install the app so they receive a genuine `(body, hmac)` pair from Shopify, and (b) be able to redirect/replay that HTTP request to the app's webhook endpoint with a modified `shopify-shop-domain` header — both are within reach of any unprivileged Shopify merchant/developer without needing the app's `client_secret` or another shop's access token.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value verified by the HMAC, or otherwise cryptographically/authoritatively associate the declared `shop` header with the verified signature before it is exposed to handlers (e.g., document/enforce that the host app must independently confirm `data.shop` is an actually-installed shop associated with the same webhook subscription, and clearly flag `request.shop`/`WebhookMetadata#shop` as unauthenticated in the API surface of `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`).

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and lets Shopify deliver a real webhook (e.g., `orders/create`), capturing the raw request: body `B` and header `shopify-hmac-sha256: H` (valid, since Shopify signed it with the app's shared secret).
2. Attacker resends the same `B`/`H` to the app's webhook endpoint but sets `shopify-shop-domain: victim.myshopify.com` (and any topic they choose, since topic also is not covered by the HMAC).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Registry.process` calls `Utils::HmacValidator.validate(request)` which only checks `B` against `H` — this passes. [4](#0-3) 
4. The handler registered for that topic receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-controlled body `B`, despite the request never having been authenticated for that shop.

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
