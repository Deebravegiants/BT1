### Title
Webhook shop identity spoofing due to HMAC not covering the `shop-domain` header — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` header — which is *not* part of the signed material — to attribute the webhook to a tenant. This breaks the identity binding `hmac_signed_bytes == data_used_for_shop_attribution`, allowing an unprivileged user who installs the app on their own store to relabel a legitimately-signed webhook payload as belonging to a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC exclusively over that signable string (the body), using the app's shared `api_secret_key`: [2](#0-1) 

`Registry.process` gates on this HMAC check and then immediately trusts `request.shop` — which is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, a value never included in the signed bytes — to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) [4](#0-3) 

Because the `api_secret_key` used to sign webhook bodies is shared across every shop that installs the app (it is not shop-specific), any user who installs the app on their own store legitimately receives a `(body, hmac)` pair that is valid under the shared secret. That same `(body, hmac)` pair remains valid HMAC-wise no matter what value is placed in the `shop-domain` header, since the header is outside the signed scope. This lets that user re-submit the payload to the app's webhook endpoint with an arbitrary victim shop's domain in the header, and the library will accept it as an authentic webhook for the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC check is meant to enforce: an app relying on `ShopifyAPI::Webhooks::Registry.process`/`WebhookMetadata#shop` to route data storage or trigger tenant-scoped side effects (e.g., updating a shop's local order/product cache, billing state, or app-uninstalled cleanup) can be made to apply attacker-supplied webhook data under another merchant's identity — a cross-tenant data injection/confusion vulnerability.

### Likelihood Explanation
Any user can install a public embedded app on their own (attacker-controlled) shop, which is a normal, unprivileged action, and thereby obtain a genuinely-signed `(body, hmac)` pair from Shopify. Crafting the replay request with a spoofed `shop-domain` header requires no secrets or privileged access — only the ability to send an HTTP POST to the app's public webhook endpoint.

### Recommendation
Bind the shop identity into the material that is authenticated, e.g., include the `shop-domain` header (and/or other identifying headers) in `to_signable_string`, or cross-validate `request.shop` against the shop embedded in the (HMAC-covered) webhook body where Shopify's payload includes it, rejecting mismatches before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify sends a legitimate webhook POST to the app's webhook endpoint:
   - Body: `{"id":123,...}` (raw JSON)
   - Headers: `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`
3. Attacker replays this exact body and HMAC to the same endpoint, only changing the header:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks the body bytes.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id":123,...})`, causing the app to process attacker-controlled data as though it originated from the victim tenant.

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
