### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the tenant identity (`shop`) that is handed to the app's webhook handler is read from an HTTP header that is never included in the signed material. Because the webhook HMAC secret (`Context.api_secret_key`) is shared across every shop that has the app installed, any shop that has installed the app can capture a validly-signed `(body, hmac)` pair from its own webhook deliveries and replay it to the app's public webhook endpoint with the `shop-domain`/`x-shopify-shop-domain` header rewritten to a victim shop. The HMAC check still passes, and the handler is invoked believing the payload came from the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is derived independently from a header that is not part of that signed string: [2](#0-1) 

`Registry.process` validates the HMAC of the request (i.e., of the body only) and then immediately trusts `request.shop` as the tenant identity forwarded to the app's handler: [3](#0-2) 

The HMAC secret used is `Context.api_secret_key`/`Context.old_api_secret_key`, which is the app's single client secret shared by all shops using the app — it is not shop-specific: [4](#0-3) 

By contrast, the OAuth callback's equivalent verifiable query (`Auth::Oauth::AuthQuery`) *does* include `shop` inside `to_signable_string`, so the shop value there is cryptographically bound to the signature: [5](#0-4) 

The webhook path breaks the equivalent binding: `shop_claimed_in_header == shop_covered_by_hmac` does not hold, because `shop_covered_by_hmac` is undefined (the signature only covers `raw_body`). This is exactly the "field acted on but not covered by the HMAC" identity-binding break called out as in-scope.

### Impact Explanation
Any entity that can install the app on a shop they control (an ordinary, unprivileged action — no `api_secret_key`, access token, or leaked credential required) can obtain arbitrarily many valid `(raw_body, hmac)` pairs, since Shopify signs every webhook delivery with the same app-level secret regardless of which shop triggered it. That attacker can then send a forged HTTP POST to the app's public webhook endpoint using a captured valid body+HMAC but with the `x-shopify-shop-domain`/`shopify-shop-domain` header set to any victim shop domain. `HmacValidator.validate` will accept it because it never inspects the header, and `Registry.process` will invoke the app's webhook handler with `WebhookMetadata#shop` set to the victim's domain. Any host application that uses this gem's documented `shop` field (as intended by the library's API) to select per-tenant session/data — the standard integration pattern — will act on the victim tenant using attacker-supplied event data, achieving cross-tenant access/confusion. This is a Critical-tier impact under the rubric (cross-tenant access) arising purely from this gem's own verification logic.

### Likelihood Explanation
Likelihood is high: the only prerequisite is installing the target public app on any shop (a normal, unprivileged, self-service action available to any merchant/attacker), after which every legitimately received webhook gives the attacker a fresh valid `(body, hmac)` pair to replay with a spoofed shop header against the same public endpoint. No secret material, token theft, or privileged access is needed.

### Recommendation
Include the shop identity (and topic) in the signed/verified material for webhooks, or independently verify that the `shop-domain` header corresponds to a shop actually entitled to trigger that specific signed payload (e.g., cross-check against a per-shop record established during OAuth, rather than trusting the header outright). At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop/topic headers so `HmacValidator.validate` cryptographically binds the claimed tenant to the signature, mirroring what `Auth::Oauth::AuthQuery#to_signable_string` already does for `shop` in the OAuth flow.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (normal, unprivileged flow).
2. Shopify delivers a legitimate webhook (e.g. `orders/create`) to the app's webhook endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(app_secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays this exact request to the same endpoint but changes only `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(app_secret, B)` from `to_signable_string` (the raw body only) — validation succeeds since `B` and the HMAC are unchanged.
5. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: B, ...)` — the app now processes attacker-controlled data attributed to `victim.myshopify.com`.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
