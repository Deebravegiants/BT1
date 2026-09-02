### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by verifying an HMAC over the raw request body, while the shop identity (`shop-domain` header) that the handler receives and treats as the authenticated tenant is never included in that signature. This breaks the intended binding `hmac_verified(payload) == shop_authenticated(payload)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from a separate, unsigned header: [2](#0-1) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` using `request.shop`, which is passed straight to the app's handler as the tenant identity, with no cross-check that the signed body actually corresponds to this shop: [3](#0-2) 

`HmacValidator.validate` only proves the request was signed with the app's `api_secret_key` (or `old_api_secret_key`) — a secret shared across *every* shop that has installed the app — using `verifiable_query.to_signable_string`, i.e., the raw body only: [4](#0-3) 

Because the webhook HMAC key (`client_secret`) is the same for all merchants/shops using a given app, and the signature covers only the JSON body (not the shop header, topic, or webhook id), a payload with a valid signature for Shop A's data can be replayed with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header changed to Shop B. `HmacValidator.validate` will still return `true` (the body and secret are unchanged), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to Shop B, even though the signed bytes were never bound to that shop. This is exactly the analog class called out in the rules: "bytes verified versus bytes parsed" / "a field acted on but not covered by the HMAC" — here the acted-upon field is the tenant-identifying `shop` value.

### Impact Explanation
This breaks the equality `authenticated_shop == shop_used_for_tenant_routing`. Any application built on top of this gem's webhook registry that uses `WebhookMetadata#shop` to decide which merchant's records to update/read (the documented and expected usage) can be made to apply an attacker-observed, validly-HMAC'd payload to a different shop's tenant context, since the header is fully attacker-controllable and the library performs no binding check. This is a cross-tenant data-integrity/confusion issue reachable by any party able to submit an HTTP request to the app's webhook endpoint with a body+HMAC pair they've observed (e.g., from a webhook fired to their own store, or from a leaked/logged payload) — no access token or `api_secret_key` is required from the attacker.

### Likelihood Explanation
Exploitability requires only observing one legitimately-delivered webhook body+HMAC pair (something an app developer or even a merchant with webhook access to their own shop can obtain), then re-POSTing it to the app's public webhook endpoint with a different `shop-domain` header value. No secrets or privileged access are needed to perform the replay itself; the gem performs no additional binding of the signed content to the claimed shop.

### Recommendation
Bind the shop identity into the verified material, e.g.:
- Include the `shop-domain` (and ideally `topic`/`webhook-id`) header value in `to_signable_string`'s signed input, or
- Independently verify that the shop asserted in the header matches a shop with an active, previously-established session/installation known to the app before trusting `WebhookMetadata#shop`, and reject the request otherwise (analogous to `require(_exists(...))` pattern from the referenced report — verify shop identity exists/matches before acting on it, don't just trust the parsed byte content).

### Proof of Concept
1. Register an app and receive a real webhook delivery for `shop-a.myshopify.com` with body `B` and header `Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(client_secret, B)`).
2. Replay the exact same raw body `B` and header `H` to the app's webhook endpoint, but set `Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (body and secret match), per [5](#0-4) .
4. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "shop-b.myshopify.com", body: parsed(B) ...)`, per [6](#0-5) , causing shop A's data to be processed under shop B's tenant context.

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
