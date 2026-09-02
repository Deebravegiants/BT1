### Title
Webhook Shop-Domain Spoofing via HMAC Signature Covering Only the Raw Body - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` value (read from the `X-Shopify-Shop-Domain` header) is never included in the signed data. `Registry.process` validates only the body-derived HMAC and then forwards the unauthenticated `shop` header directly to the app's webhook handler as the tenant identifier. This breaks the binding `hmac_signed_bytes == identity_used_for_routing`, letting a merchant who possesses one genuine, validly-signed webhook payload (signed with the app's single, shop-agnostic `client_secret`) relabel it as coming from a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature strictly from `to_signable_string` and compares it to the `hmac` header via `OpenSSL.secure_compare`: [2](#0-1) 

`Registry.process` validates this HMAC and then trusts `request.shop` — sourced from the unauthenticated `shopify-shop-domain` header — as the tenant identity passed to the app's handler: [3](#0-2) 

Because Shopify signs webhooks for every shop installed on an app using the same app-level `client_secret` (the constant used in `HmacValidator.validate` is `Context.api_secret_key`, not a per-shop secret), a valid `(raw_body, hmac)` pair generated for one shop remains valid for the exact same body regardless of which `shop` header accompanies it. The identity check (`hmac` valid) and the identity actually used (`shop` header) are not bound together, so an attacker can decouple them.

### Impact Explanation
An unprivileged merchant who has their own shop with the app installed can capture a genuine webhook delivery (body + `X-Shopify-Hmac-Sha256` header) sent by Shopify for their own store. By replaying that exact body/HMAC pair while substituting a victim shop's domain in the `shopify-shop-domain` header, they obtain a request that passes `HmacValidator.validate` and is delivered to the app's handler tagged with the victim's shop. This is a cross-tenant identity-spoofing primitive: any host application that keys data storage, authorization, or state transitions off `WebhookMetadata#shop` (as the documented/intended usage pattern) can be made to apply attacker-controlled webhook data to another tenant's records, including mandatory-compliance topics like `customers/redact` or `shop/redact`. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high for any installed, unprivileged merchant: obtaining one legitimate webhook for their own shop requires no special privilege (merely having the app installed, e.g. via a public app listing), and replaying an HTTP request with a modified header is trivial. The only constraint is that the replayed body's content must still make sense for the impersonated shop's context in the host app, which is often satisfiable for generic/compliance topics or where the app trusts `shop` for row/tenant selection without further validation of body contents.

### Recommendation
Include the `shop` (and ideally `topic`) values in the HMAC-signed payload verification, e.g. by binding the signature check to `"#{shop}\n#{raw_body}"` or by having `HmacValidator`/`Request` cross-check that `shop` matches an independently trusted value (such as looking up the session/shop the app expects for that webhook subscription) rather than trusting the header value as-is once the body-only HMAC passes. At minimum, document that `shop` from `WebhookMetadata` must not be trusted as an authenticated tenant identifier unless additionally verified.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com` and trigger a webhook (e.g. `orders/create`) to receive a genuine delivery with body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's single `client_secret`).
2. Replay the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` (`B`) only and matches `H`, so validation succeeds: [4](#0-3) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from `attacker-shop.myshopify.com`, demonstrating the cross-tenant identity spoof.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
