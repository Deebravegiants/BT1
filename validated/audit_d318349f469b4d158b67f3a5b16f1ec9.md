## Title
Webhook HMAC Does Not Bind the `shop-domain` Header, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable content from the raw body only, while the `shop` (tenant identity) is read from a separate, unsigned header. Because the webhook HMAC secret (`Context.api_secret_key`) is shared across *all* shops that install the app, any shop that can produce a validly-signed webhook (i.e. any of the app's own merchants) can replay that exact body/HMAC pair while swapping the `shop-domain` header to claim to be a different, victim shop. The identity binding `authenticated(bytes) == attributed_shop` is broken.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

But `shop` is pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed content: [2](#0-1) 

`Registry.process` validates only this body HMAC and then unconditionally trusts `request.shop` to attribute the event to a tenant when dispatching to the handler: [3](#0-2) 

`HmacValidator.validate` signs/verifies with `Context.api_secret_key`, which is the **app-wide** secret — identical for every shop that has installed the app, not a per-shop secret: [4](#0-3) 

Because the secret is shared across tenants and the signature covers only the body, an attacker who is a legitimate (but unprivileged, from the victim's perspective) merchant of the same app can:
1. Trigger a real webhook from Shopify to their own shop (e.g. by editing a product/customer/order field they control), receiving a body + valid `x-shopify-hmac-sha256` for their own shop.
2. Replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint, but with the `shop-domain` header rewritten to the victim's shop domain.
3. `HmacValidator.validate` still succeeds because it only checks the body bytes against the shared secret — the shop header was never part of what was signed.
4. `Registry.process` calls the handler with `WebhookMetadata` carrying the forged victim shop, causing the app to act on the victim tenant's data using attacker-supplied (but nominally validated) content — e.g. an `app/uninstalled` handler could delete/revoke the victim shop's stored session/access token, or a data-processing handler could write attacker content into the victim's tenant records.

### Impact Explanation
This is a cross-tenant access vulnerability: an app built on this gem trusts `request.shop` as an authenticated tenant identifier once `HmacValidator.validate` passes, but that field is never covered by the HMAC. An unprivileged user who merely has their own install of the app can forge webhook deliveries attributed to any other merchant's shop, potentially triggering destructive or data-corrupting actions (e.g. uninstall/token-revocation handling, or writing forged data) against a shop they do not control — a Critical-class cross-tenant impact per the given rubric.

### Likelihood Explanation
Any app developer using this gem's documented webhook API (`Webhooks::Request.new` + `Webhooks::Registry.process`) is exposed as-is, without any misuse of the API. The attacker only needs a real install of the target app on their own store (any customer of the app qualifies) to obtain a validly-HMAC-signed payload, plus the ability to POST directly to the app's public webhook endpoint with a custom header — both trivially available to any internet user interacting with the app as a merchant.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed body (e.g., include the shop domain in `to_signable_string`, or require callers to independently verify that `request.shop` corresponds to a shop with a currently stored, valid session/access token before trusting it as a tenant identifier).

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger a webhook (e.g. `products/update`) so Shopify sends a real request with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Capture `B` and the HMAC value.
3. POST to the app's public webhook endpoint with the same body `B` and same HMAC header, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) returns `true` since it only checks `B` against the shared `api_secret_key`.
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, processing attacker-controlled content as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
