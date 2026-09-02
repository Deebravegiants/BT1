### Title
Webhook `shop` identity is taken from an unauthenticated header while the HMAC only covers the raw body, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw request body, but it then trusts a separate, unsigned header (`shopify-shop-domain`/`x-shopify-shop-domain`) as the tenant identity passed to the app's handler. Because the HMAC signature does not bind the `shop` value, an attacker who legitimately receives one valid signed webhook (e.g., for their own store) can replay the same body/HMAC pair while substituting the `shop-domain` header for a victim shop, and the gem will accept it as authentic.

### Finding Description
`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the registered handler: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [2](#0-1) [3](#0-2) 

The `shop` accessor, however, is read straight from the HTTP header without any cryptographic binding to the HMAC: [4](#0-3) 

That unverified `shop` value is then forwarded directly into the dispatched `WebhookMetadata` that the host application's handler acts on: [1](#0-0) 

This breaks the identity binding that the report's bug class targets: `HMAC-covered bytes == identity used downstream`. Here, `HMAC(raw_body)` is verified, but `request.shop` (the field actually acted upon by the app's webhook handler to decide which tenant's data to touch) is not part of what the HMAC signs. Concretely: **bytes verified (`raw_body`) != identity trusted (`shop-domain` header)**.

### Impact Explanation
Any party who can obtain one legitimately-signed webhook body/HMAC pair (trivially available to any merchant who installs the app on their own store and receives webhooks from Shopify) can resend that exact body/HMAC to the app's webhook endpoint while swapping the `shop-domain` header to a different, victim shop domain. Because `Registry.process` never re-derives or checks that the HMAC is scoped to the claimed shop, the forged request passes validation and is routed to the handler tagged with the victim's shop domain. If the host application uses `WebhookMetadata#shop` to select which tenant's session/data to update (the documented purpose of this field), this yields cross-tenant data confusion/access — one merchant can inject fabricated webhook events attributed to another merchant's shop, without holding that shop's credentials.

### Likelihood Explanation
Low-to-medium likelihood: it requires the attacker to already have at least one legitimately signed webhook payload (obtainable by installing the app themselves, a normal unprivileged action) and to know or guess a target `shop` domain (public information, i.e., `*.myshopify.com` names). No `api_secret_key`, access token, or privileged access is needed — the attacker never needs the secret because they reuse a genuine signature rather than forging one.

### Recommendation
Bind the shop identity into the signed material, or otherwise verify it out-of-band. Concretely: include the `shop-domain` (and/or `topic`, `webhook-id`) header value in `Webhooks::Request#to_signable_string` (as Shopify's own HMAC signing already implicitly ties to a specific shop delivery in the real service, this gem's local re-validation should not just check the body) — or, at minimum, document and enforce that consuming handlers must cross-check `data.shop` against a shop that is independently known to be associated with the request context (e.g., a session or webhook subscription lookup) before trusting it for tenant-scoped side effects.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and captures one real webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's `api_secret_key`), plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only (`to_signable_string` returns `@raw_body`) — validation succeeds because the body/HMAC pair is unchanged. [2](#0-1) 
4. `Registry.process` dispatches to the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, where `request.shop` now returns `"victim-shop.myshopify.com"`. [5](#0-4) 
5. Any handler logic keyed on `data.shop` (e.g., updating per-shop records, triggering tenant-scoped side effects) now operates against the victim shop's identity based on a request the attacker fully controlled.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
