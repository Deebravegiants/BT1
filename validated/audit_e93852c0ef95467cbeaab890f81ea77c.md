This confirms the finding. The `HmacValidator.validate` only checks `hmac(raw_body, secret)` via `Request#to_signable_string`, which returns `@raw_body` alone — the `shop-domain` header used as `request.shop` is never part of the signed bytes.

### Title
Webhook Shop Identity Not Bound to HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop` value (used downstream to identify the tenant) is read from the unsigned `X-Shopify-Shop-Domain` header. `Registry.process` validates only that the HMAC matches the body, then passes the header-derived `shop` straight into `WebhookMetadata` for the app's handler, breaking the intended binding: `hmac == HMAC(body_bytes_only)` while the app's tenant-routing logic implicitly assumes `hmac` authenticates `(body, shop)` together.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `Request#shop` is pulled from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (the raw body only) and compares it against the secret-derived signature: [3](#0-2) 

After a successful HMAC check, `Registry.process` forwards the unsigned, attacker-controllable `request.shop` value directly to the handler as the tenant identifier: [4](#0-3) 

Because `shop` is excluded from the signed bytes, the identity binding `hmac ⇒ (body, shop)` does not hold — only `hmac ⇒ body` holds. Any party who can obtain one validly-signed `(body, hmac)` pair from Shopify (e.g., a merchant installing the same multi-tenant app, who legitimately receives their own signed webhooks) can replay that exact body/hmac pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. The HMAC still validates because it never covered the shop field, yet the app's handler will process the payload as if it belongs to the attacker-chosen shop.

### Impact Explanation
This breaks the tenant/shop authentication boundary that HMAC verification is meant to enforce for multi-tenant apps built on this gem: a request cryptographically proven to come from Shopify for shop A can be relabeled as belonging to shop B purely by header manipulation, with no shop-secret knowledge required. Any app relying on `WebhookMetadata#shop` (as returned by the gem's own `Registry.process` API) to select which tenant's data to create/update/delete will act on the wrong tenant, causing cross-tenant data confusion. This matches the Critical "cross-tenant access" impact category, since it's the gem's own signature-validation and metadata-dispatch code that produces the attacker-controlled, unauthenticated tenant identifier.

### Likelihood Explanation
Exploitation only requires the attacker to control (or briefly observe) one legitimate installed shop of the target app in order to obtain a validly-signed webhook body/HMAC pair — no access to the app's `client_secret` is needed, and no interaction with a victim shop is required, since the attacker simply resends their own valid request with a different `shop-domain` header value. Any app that trusts `request.shop`/`WebhookMetadata#shop` from this gem without independently cross-checking it against a known, previously-registered shop for that specific webhook body is exposed.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the `shop-domain` header to the verified payload before it is trusted:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` verification if Shopify's signature scheme allows verifying headers, or
- At minimum, document/enforce that consuming apps must independently validate `request.shop` against the shop that owns the specific webhook subscription (e.g., by looking up `webhook_id` or by storing an app-side webhook secret/nonce keyed per shop) rather than trusting the header value emitted by `Registry.process`.
- Consider raising `Errors::InvalidWebhookError` in `Registry.process` when the `shop` header does not match an app-known, currently-installed shop.

### Proof of Concept
1. App is a multi-tenant Shopify app built on this gem, receiving `orders/create` webhooks at `/webhooks` for many installed shops.
2. Attacker installs the app on their own shop `attacker-shop.myshopify.com` and creates an order, causing Shopify to POST a legitimately HMAC-signed webhook:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-signature-for-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id":123,...}
   ```
3. Attacker captures this exact body and `X-Shopify-Hmac-Sha256` value (both are visible to them since it's their own shop).
4. Attacker resends the identical body and HMAC header to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) succeeds because it only checks `HMAC(raw_body)`, which is unchanged.
6. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"`, even though Shopify never sent this webhook for that shop — demonstrating the app-facing API of this gem hands the handler an unauthenticated, spoofable tenant identifier.

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
