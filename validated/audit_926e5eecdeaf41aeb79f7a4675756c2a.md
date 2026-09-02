### Title
Webhook `shop` identity is trusted from an unauthenticated header not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw request body, then hands the handler a `WebhookMetadata` struct whose `shop` field is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header. That header is never included in the signed material, so the HMAC check proves the *body* is untampered but proves nothing about which shop the body belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate`/`validate_signature` compute and compare the HMAC exclusively against `verifiable_query.to_signable_string`: [2](#0-1) 

Meanwhile `shop` is read straight from an HTTP header with no cryptographic binding to the body/HMAC: [3](#0-2) 

`Registry.process` validates the HMAC, then immediately trusts `request.shop` as the tenant identity for the handler, without any check that the shop header is consistent with the signed body: [4](#0-3) 

The identity binding that the library's API contract implies is:
`verified_shop (bound by HMAC over the payload) == attributed_shop (WebhookMetadata.shop delivered to the app's handler)`

In reality the equality is: `attributed_shop = request.shop` (unauthenticated header), while `verified_shop` is undefined — the HMAC only proves body integrity, not shop origin. An attacker who can produce (or capture) any single valid `(raw_body, hmac)` pair signed with the app's secret — e.g. from a legitimate webhook delivered to their own shop after installing the app — can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because it only checks `@raw_body`, and `Registry.process` forwards `WebhookMetadata.new(shop: request.shop, ...)` to the app's handler, which will process/store the (attacker-supplied) body under the victim's tenant identity.

### Impact Explanation
This breaks the tenant/authentication boundary the webhook pipeline is expected to enforce: an unprivileged holder of one valid shop-signed payload can cause the app to process or persist arbitrary body content attributed to a different (victim) shop. Since most multi-tenant Shopify apps key their business logic, storage, and side effects (e.g., `perform_later(shop_domain: data.shop, webhook: data.body)`, as shown in the gem's own documented handler pattern) directly off `WebhookMetadata.shop`, this is a cross-tenant data-integrity/confusion issue — data belonging to shop A can be injected into shop B's context purely because the `shop` field sits outside the HMAC's protected scope. [5](#0-4) 

### Likelihood Explanation
Low/Medium: it requires the attacker to already be able to obtain one legitimately-signed `(body, HMAC)` pair for the *same app* (e.g., by installing the app on their own shop and capturing a webhook delivery), and requires the target app to expose a single shared webhook endpoint used across tenants (a common pattern this gem's docs describe with one `Registry.process` call per handler, not per shop). No `api_secret_key`, access token, or TLS interception is required — only network access to the app's public webhook route and a previously-observed valid webhook delivery.

### Recommendation
Bind the trusted `shop` value to the authenticated payload instead of trusting a bare header:
- Include the shop domain (and ideally topic/webhook-id) as part of the signed/verified material, or
- Independently validate that `request.shop` matches a shop known to be associated with the specific HMAC/topic/webhook-id combination (e.g., cross-check against the shop's own stored secret/session rather than a single shared app secret), or
- At minimum, document/require host applications to treat `WebhookMetadata.shop` as untrusted unless additionally corroborated, and update `HmacValidator`/`Webhooks::Request#to_signable_string` so the shop-domain header participates in the signature check.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: headers include `x-shopify-hmac-sha256: <H>` and `x-shopify-shop-domain: attacker.myshopify.com`, with some raw body `B`. `H = HMAC-SHA256(api_secret_key, B)`.
2. Resend the exact same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B)` (per `lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`) — it matches `H`, so validation passes.
4. `ShopifyAPI::Webhooks::Registry.process` calls the app handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing attacker-controlled body content to be processed under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
