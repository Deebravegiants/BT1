### Title
Webhook shop-domain header is trusted for tenant identification but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts the `shop` (`x-shopify-shop-domain` / `shopify-shop-domain`) header and passes it downstream as the authoritative tenant identifier for a webhook, but `Utils::HmacValidator` only signs/verifies the raw request body. Any attacker who can obtain one valid `(body, hmac)` pair signed with the app's shared secret can replay it to the app's webhook endpoint while substituting the `shop-domain` header for a different (victim) shop, and the HMAC check will still pass.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
`shop` is read directly from a header that is never part of the signed data: [2](#0-1) 

`Utils::HmacValidator.validate` only compares the computed signature against `verifiable_query.to_signable_string`, i.e. body bytes, with the app's single shared `Context.api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` using the unverified `request.shop` value, handing it to the host app's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

The gem's own documentation instructs apps to key downstream work off `data.shop` exactly as returned by this unverified header: [6](#0-5) 

This is the identity-binding break: the equality the code implicitly assumes is `shop header == tenant that produced the signed body`, but the HMAC only proves `body bytes == body bytes signed by the app's secret`; it says nothing about which shop that body belongs to. Because a single app-wide `api_secret_key` (not a per-shop secret) is used to sign all webhooks, any body/HMAC pair valid for one shop is also a valid signature for a request claiming to be from any other shop — the signature is shop-independent.

### Impact Explanation
An attacker who operates (or has installed) the app on their own shop can generate legitimate webhooks for their own tenant (e.g. `orders/create`), capture the resulting `(raw_body, hmac)` pair, and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. Because the signature check only validates body integrity against the shared secret — not the shop claim — the forged request passes verification and the host app processes attacker-controlled webhook data under the identity of a different, victim tenant. Per the documented usage pattern, this data flows directly into per-shop background jobs and business logic keyed by `data.shop`, producing cross-tenant data injection/confusion.

### Likelihood Explanation
Requires no possession of `api_secret_key` or access token: the attacker only needs to be an authenticated merchant/user of the app (to receive at least one legitimate webhook) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint with modified headers — both are unprivileged-internet-user capabilities relative to any other tenant.

### Recommendation
Bind the shop identity into what is cryptographically verified: either include the shop domain in the signed payload/signable string used by `HmacValidator`, or require registry/consumers to independently verify that the `shop` header's webhook subscription/id (`webhook_id`) actually corresponds to a subscription registered for that shop before trusting `WebhookMetadata#shop`, and document that host apps must not treat the header value as authenticated without this additional check.

### Proof of Concept
1. Install/authorize the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) to receive a legitimate `POST` with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac>`, and raw body `B`.
2. Replay the exact same request to the app's webhook route, changing only `x-shopify-shop-domain` to `victim.myshopify.com` (all other headers/body unchanged).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which recomputes HMAC over `raw_body` (`B`) with the shared `Context.api_secret_key` — identical to step 1 — so validation succeeds.
4. The handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com", body: <attacker's body> ...)`, and the host app (per documented usage) processes/persists this data as if it originated from `victim.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
