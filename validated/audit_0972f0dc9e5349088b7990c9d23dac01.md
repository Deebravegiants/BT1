### Title
Webhook shop-domain header is trusted for tenant identification without being covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (tenant identifier) is read from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` verifies only the HMAC of the body and then hands `request.shop` straight to the app's webhook handler as the tenant identity. Because the HMAC secret (`Context.api_secret_key`) is the same for every merchant shop that has installed the app, any shop that can generate one legitimate webhook (by triggering an event in its own store) obtains a valid `(body, hmac)` pair that remains valid no matter what `shop-domain` header value accompanies it. This breaks the equality that should hold: `shop authenticated by HMAC == shop used as tenant/session key`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` as the tenant to pass into the app's handler, with no additional check binding the verified body to the claimed shop: [3](#0-2) 

`HmacValidator.validate` computes the signature using `Context.api_secret_key` (the single client secret shared by the app across *all* installed shops), independent of any shop identifier: [4](#0-3) 

Because the same secret validates the same body regardless of which shop sent it, and the `shop` header sits entirely outside the signed content, the equality the gem should guarantee — `hmac_verified(body) → shop_header == originating_shop` — does not hold. Any tenant of the app can capture one of its own valid `(raw_body, x-shopify-hmac-sha256)` pairs (e.g., by triggering an `orders/create` event in its own store) and replay it to the shared webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks the body against the shared secret, and `Registry.process` will invoke the registered handler with `WebhookMetadata` carrying the attacker-chosen `shop` value: [5](#0-4) 

Any host application that uses `request.shop` from a processed webhook to look up a session, update tenant-scoped data, or otherwise key work by shop (a documented and expected usage pattern of this field) will act on forged data attributed to an arbitrary victim shop.

### Impact Explanation
This is a cross-tenant boundary break: a single unprivileged merchant that has installed the app can forge webhook events that authenticate (via valid HMAC) but are misattributed to any other shop using the same app. Depending on how the host app consumes `WebhookMetadata#shop`/`WebhookMetadata#body` (e.g., updating orders, redacting customer data for GDPR topics, syncing inventory), this enables injection of attacker-controlled data into another tenant's records — cross-tenant access, which is classified as Critical impact per the rules.

### Likelihood Explanation
Likelihood is high for any app that shares one HTTP webhook endpoint across all installed shops (the standard, documented Shopify app topology) and reads `request.shop` to determine tenant context, which is the field's documented purpose in `WebhookMetadata`. The attacker only needs their own legitimate app installation to generate one valid `(body, hmac)` pair per topic of interest; no access to the `api_secret_key`, any access token, or another merchant's credentials is required — only replaying an HTTP request with a modified header.

### Recommendation
Bind the shop to the verified signature: include the `shop`/`shop-domain` value (and ideally `topic`, `webhook_id`) in `Request#to_signable_string`, or otherwise incorporate the shop-domain header into the value that `HmacValidator` verifies, so that a body signed for one shop cannot be replayed under a different shop's identity. At minimum, document prominently that `request.shop` is not covered by the HMAC and must not be trusted as an authenticated tenant key without an independent verification step (e.g., cross-checking against a known/registered shop for that webhook subscription).

### Proof of Concept
1. App `X` is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`, sharing one webhook endpoint and one `api_secret_key`.
2. Attacker controls `shop-a.myshopify.com`. They trigger an `orders/create` event in their own store, which Shopify sends to the app's endpoint with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and the JSON body.
3. Attacker captures this exact `raw_body` + `x-shopify-hmac-sha256` pair.
4. Attacker replays the identical request to the same endpoint, changing only `x-shopify-shop-domain` to `shop-b.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged headers/body; `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes the HMAC over `raw_body` with the shared secret — see `to_signable_string` at [1](#0-0) .
6. `Registry.process` invokes the registered handler with `shop: "shop-b.myshopify.com"` and the attacker-controlled body — see [5](#0-4) , causing the host app to process forged data as if it originated from `shop-b`.

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
