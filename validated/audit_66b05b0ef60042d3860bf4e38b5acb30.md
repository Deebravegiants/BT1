Confirmed: `ShopifyAPI::Webhooks::Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, while `#hmac` verification (`Utils::HmacValidator.validate`) is computed only over `to_signable_string`, which returns `@raw_body` — the shop-domain header is never part of the signed material.### Title
Webhook `shop-domain` header is trusted for tenant routing without being covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity attribute purely from an unauthenticated HTTP header, while the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates only covers the raw request body. Because the app's `api_secret_key` is shared across all shops using the app, anyone who is a legitimate merchant of the app (and thus receives genuine, validly-signed webhooks for their own store) can replay that same `(raw_body, hmac)` pair to the app's public webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to a victim shop's domain, and the HMAC check will still pass.

### Finding Description
`Registry.process` only calls `Utils::HmacValidator.validate(request)` before dispatching to the handler: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` using the single, app-wide `Context.api_secret_key`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 

but the `shop` accessor — which becomes the tenant identity passed to the handler as `WebhookMetadata#shop` — is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never part of the signed material: [4](#0-3) [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `shop header == shop bound by HMAC`. In fact, `HmacValidator.validate` only proves `hmac == HMAC(api_secret_key, raw_body)`; it says nothing about which shop the `(raw_body, hmac)` pair belongs to. Since `api_secret_key` is one value per app (not per shop), any tenant of the app that legitimately installs it and receives real webhooks obtains a valid `(raw_body, hmac)` pair for their own shop. That attacker-tenant can then send a forged HTTP request directly to the app's webhook endpoint containing the same `raw_body`/`hmac`, but with the `shop-domain` header rewritten to point at a different (victim) shop. `Registry.process` will validate the HMAC successfully (it only checks the body) and will call the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain, even though the payload was never sent by Shopify on behalf of that shop.

### Impact Explanation
This breaks the tenant isolation the whole webhook mechanism is meant to enforce: the gem authenticates "this body was HMAC'd with our app secret" but the caller of `Registry.process` (i.e., every app built on this gem, following the documented `WebhookController` pattern) is led to believe `data.shop` is equally authenticated. Any app that keys per-tenant side effects (writing to shop-specific tables, updating shop-specific inventory/orders, dispatching background jobs scoped `shop_domain: data.shop` as shown in the gem's own docs) off `WebhookMetadata#shop` is vulnerable to cross-tenant data injection/corruption driven by an attacker who is merely a legitimate (potentially free-tier) installer of the app. This matches "cross-tenant access" in the impact taxonomy, and it is a root-cause issue in the gem's own `Request`/`Registry`/`HmacValidator` — not a misuse of the documented API, since the documented usage (`Registry.process(Request.new(...))`) is exactly what is shown in `docs/usage/webhooks.md`.

### Likelihood Explanation
Exploitation requires the attacker to be a legitimate merchant/tenant of the target app (to obtain at least one valid, real webhook body+HMAC pair for their own shop) and to be able to send arbitrary HTTP requests to the app's public webhook endpoint (which is, by design, internet-reachable and unauthenticated aside from the HMAC check). No access to `api_secret_key`, access tokens, or other credentials is required. This is a realistic scenario for any multi-tenant Shopify app, since installing an app is a self-service action.

### Recommendation
Bind the `shop` field into the material that is HMAC-verified (or otherwise independently authenticate the shop for each webhook), for example:
- Include the `shop-domain` (and ideally `webhook-id`/`topic`) header value in `to_signable_string` for `Webhooks::Request`, matching how the header is bound in the signature the way Shopify does for OAuth callbacks (`AuthQuery#to_signable_string` includes `shop`).
- Alternatively, cross-check the `shop` derived from the header against an independently-verified source (e.g., the shop associated with the specific webhook subscription id) before dispatching to the handler.
- At minimum, document loudly that `data.shop` from `WebhookMetadata` is *not* cryptographically authenticated on its own and must not be trusted for authorization decisions without additional verification (e.g., confirming a session/webhook subscription actually exists for that shop).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook, e.g., for `orders/create`, with body `B` and headers including `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared `api_secret_key`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker sends a new HTTP POST directly to the app's public webhook endpoint (the one wired to `ShopifyAPI::Webhooks::Registry.process`), with the exact same body `B` and `x-shopify-hmac-sha256: H`, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(api_secret_key, B)` and compares to `H` — matches, since only the body is signed: [7](#0-6) 
4. `Registry.process` proceeds and invokes the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, i.e., the attacker's own order payload is now attributed to `victim-shop.myshopify.com` in the app's business logic: [8](#0-7)

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
