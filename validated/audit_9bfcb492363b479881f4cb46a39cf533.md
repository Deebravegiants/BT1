### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the `shop` (tenant) identifier is read from an HTTP header that is never included in that signature. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts the header-derived `shop` value to route/tag the webhook data. Anyone who can generate one genuinely-signed webhook (e.g. the operator of their own installed shop, which is an unprivileged action) can replay that exact body with a different `shopify-shop-domain` header and the signature will still validate, letting them attribute the payload to an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` values are all pulled straight from headers and are never mixed into the signed string: [2](#0-1) 

`Registry.process` validates the HMAC of the request (i.e., of the body only) and, once that passes, unconditionally forwards the header-derived `shop` to the registered handler as the authoritative tenant identifier: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` confirm only that `HMAC(secret, raw_body) == received_signature` — the shop is never part of the equality being checked: [4](#0-3) 

This breaks the intended identity binding:
`hmac_valid == (HMAC(secret, body) == signature)`, but the app-facing decision actually made is `trusted_shop == header["shopify-shop-domain"]`, with no equality tying the signature to that shop. Since the `api_secret_key` (the app's `client_secret`) is the same for every shop that installs the app, two different tenants produce indistinguishable signatures for the same body. Any merchant who installs the app on their own shop and captures one of their own legitimately-signed webhook deliveries (a normal event they can trigger themselves, e.g. an order update) can resend that exact `body + hmac` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a different, victim shop's domain. `HmacValidator.validate` still returns `true` because it only recomputes the HMAC over the body, and `Registry.process` passes the attacker-chosen `shop` through to `WebhookMetadata` untouched.

### Impact Explanation
This is a cross-tenant access issue: an unprivileged attacker (any merchant who installs the app) can make the host application process webhook data under the identity of an arbitrary other shop, without ever needing that shop's credentials. Depending on how the host app's handler uses `data.shop` (e.g., to look up/write shop-scoped records), this can lead to cross-tenant data corruption or disclosure — directly matching the "cross-tenant access" critical-impact category, since the binding between the signed payload and the shop that is credited with sending it does not actually exist in this gem's verification logic.

### Likelihood Explanation
Exploitation only requires the attacker to control one legitimately installed shop (trivial, self-service on Shopify) and to be able to trigger or capture one webhook delivery with a body they can reproduce (many webhook topics have low-entropy or attacker-influenced bodies, e.g. `app/uninstalled`, or bodies that are largely static/predictable). No secret material, TLS interception, or privileged account is required — only the ability to POST to the app's public webhook endpoint with a modified header, which any internet client can do.

### Recommendation
Include the tenant-identifying fields (at minimum `shop`) in the value that is HMAC-verified, or otherwise cryptographically bind the shop header to the signature (e.g., Shopify's own webhook signing already covers the body; the gem should additionally require that the `shop` header match a shop the app actually expects, and/or the host app should independently verify shop context against a known active session before trusting `data.shop`). At minimum, document explicitly and provide a helper that ties `request.shop` verification into `HmacValidator.validate`, rather than leaving header trust implicit and unverified in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and captures a legitimate webhook delivery for topic `X`: body `B`, header `shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`).
2. Attacker resends the same `B`/`H` to the app's public webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop: "victim-shop.myshopify.com", hmac: H...})` is constructed.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and finds it equals `H` — validation passes even though the shop header was changed.
5. `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...))` is invoked, and the host application now processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
