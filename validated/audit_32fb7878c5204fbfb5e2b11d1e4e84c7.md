## Title
Webhook `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw HTTP body only, while the shop identity (`shop-domain` header), event `topic`, `webhook-id`, and `api-version` are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` validates only that the body's HMAC is correct and then dispatches to the app's handler using these unverified header values, breaking the binding between "HMAC-authenticated bytes" and "the shop/topic the app acts on."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from HTTP headers that are not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over `raw_body` only) and then builds `WebhookMetadata` straight from these unauthenticated header values before invoking the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` compares `verifiable_query.hmac` against a signature computed from `to_signable_string` (the raw body) only, never incorporating headers: [4](#0-3) 

This is precisely the "field acted on but not covered by the HMAC" bug class: the equality the code implicitly assumes is `shop == HMAC-authenticated shop`, but in reality `shop == unauthenticated header value`, since the HMAC secret (`api_secret_key`) is shared across every shop that has the app installed, and the signature never binds to which shop/topic the body belongs to.

### Impact Explanation
Any unprivileged merchant who has this app installed on their own store can legitimately trigger a webhook delivery to the app's endpoint (e.g. by performing an action, or via Shopify's webhook test feature) and capture a genuinely-HMAC-valid `(raw_body, hmac)` pair. Because the signature covers only `raw_body`, the attacker can freely resend that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header for a victim shop (and/or the `topic` header to hit a different handler), and `Registry.process` will treat it as an authentic webhook for the victim's shop. This is a cross-tenant spoofing/injection primitive: the app's business logic (order/customer/app-uninstall handling, billing state changes, etc., depending on what handlers do with `WebhookMetadata#shop`) will process attacker-controlled data attributed to an arbitrary other tenant, achieving cross-tenant access/injection without needing `api_secret_key`, an access token, or any elevated privilege — only the ability to install the app on one's own store, which is by definition an "unprivileged internet user" relative to other tenants.

### Likelihood Explanation
Likelihood is high in any app whose webhook handlers key business logic off `WebhookMetadata#shop`/`topic` without independent verification (which is the intended, documented usage pattern shown in `docs/usage/webhooks.md`). No secret material is required — only capturing one legitimate webhook delivery to the attacker's own shop and replaying it with modified headers, which requires no special tooling beyond a basic HTTP client.

### Recommendation
Bind the shop, topic, and webhook id into the material that is HMAC-verified (or independently authenticate them, e.g. by validating `shop` against the session/shop the app expects for that specific installation, and rejecting mismatches), rather than trusting header values that sit outside the signed payload. At minimum, `Registry.process` should not rely on `request.shop`/`request.topic` as authoritative for tenant identification without corroboration against a known, previously-registered value for that specific delivery.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` (or any legitimately-installed shop).
2. Attacker triggers/receives one real webhook delivery, capturing `raw_body` and its valid `X-Shopify-Hmac-Sha256` header (both computed with the app's single, global `api_secret_key`).
3. Attacker resends the identical `raw_body` and `hmac` header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally changes `X-Shopify-Topic`).
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the HMAC.
5. `Registry.process` dispatches to the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: attacker_controlled_body, ...)`, causing the app to process attacker-controlled data as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
