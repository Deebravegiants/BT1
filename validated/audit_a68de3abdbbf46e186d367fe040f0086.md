Confirmed: for OAuth's `AuthQuery`, `shop` is included in `to_signable_string` [1](#0-0) , so the shop identity is bound to the HMAC there. But for webhooks, `Request#to_signable_string` returns only `@raw_body`, excluding the `shop-domain` header entirely from the signed content [2](#0-1) , while `Request#shop` is read directly from the unauthenticated header [3](#0-2)  and is trusted downstream by `Registry.process` to build `WebhookMetadata` handed to the app's handler [4](#0-3) .

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, never including the `shopify-shop-domain` header. `Registry.process` trusts `request.shop` (sourced straight from that header) to attribute the webhook payload to a tenant when invoking the app's handler, even though that field is not bound by the cryptographic signature.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it to the `hmac` field with `OpenSSL.secure_compare` [5](#0-4) . For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns solely `@raw_body` [2](#0-1) . The `shop` accessor used elsewhere is parsed from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is attacker-controllable transport metadata, not covered by the signature [3](#0-2) .

`Registry.process` calls `Utils::HmacValidator.validate(request)` and, if it passes, builds `WebhookMetadata` using `request.shop` verbatim before dispatching to the registered handler [4](#0-3) . This breaks the intended identity binding: `hmac_valid == true` should imply `(body, shop)` were jointly authenticated by Shopify, but here it only implies `body` was signed by *some* holder of `Context.api_secret_key` — the `shop` value is asserted, not proven.

This is the direct analog of the reported Well-token uniqueness bug: there, `skim()` trusted `balanceOf()` for a token slot without verifying token-slot uniqueness/binding, letting an attacker exploit unchecked identity of a "duplicate" token. Here, `Registry.process` trusts the `shop` header as the tenant identity for a payload without that header being cryptographically bound to the signed body, letting an attacker substitute the tenant identity while keeping a valid signature.

Because a single app-level `Context.api_secret_key` is used to validate webhooks for *all* shops that installed the app (Shopify does not use a per-shop webhook secret), any attacker who controls one legitimate shop installation of the app can obtain validly-signed webhook deliveries (body + hmac) for their own tenant, then replay that exact body/hmac pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop. `HmacValidator.validate` will still pass because the header is outside the signed content, and the app's handler will process attacker-controlled body content as if it originated from the victim shop.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to look up or mutate per-tenant state (a documented and expected usage pattern for this gem, since `shop` is the field the gem exposes precisely for that purpose), an attacker can inject attacker-chosen webhook body content attributed to a victim shop, i.e., cross-tenant access/data corruption without needing the victim's credentials or access token. This matches the Critical impact category of cross-tenant access.

### Likelihood Explanation
The attacker only needs their own legitimate (even free/dev) installation of the target app to receive a validly-HMAC'd webhook for an arbitrary topic and body they can influence (e.g., via their own store's `metafields`, `orders`, or `carts` triggering a webhook whose body they control), then replay it with a forged shop-domain header at the app's public webhook endpoint. No secret material belonging to the victim is required — only network access to the app's public webhook URL, which is the intended entry point for this feature.

### Recommendation
Bind the tenant identity into the signed content that `Utils::HmacValidator` verifies for webhooks, mirroring what `Auth::Oauth::AuthQuery#to_signable_string` already does for `shop`. Concretely, `ShopifyAPI::Webhooks::Request#to_signable_string` should incorporate `shopify-shop-domain` (and ideally `topic`/`webhook-id`) into the value that is HMAC-verified, or `Registry.process` should independently confirm that the shop the app expects at that endpoint/handler matches an authenticated value, not solely a raw header. At minimum, document prominently that `request.shop` is not authenticated by the HMAC and must not be used as the sole tenant key without additional verification (e.g., cross-checking against a known/expected shop for that installation).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook topic whose body content they control (e.g., a metafield/product update) so Shopify sends a webhook with a body `B` and a valid `hmac` computed with the app's shared `Context.api_secret_key`.
3. Attacker captures `B` and the `shopify-hmac-sha256` header from that legitimate delivery.
4. Attacker POSTs the same `B` and same HMAC header to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)` which recomputes the HMAC over `@raw_body` only (`to_signable_string` in `lib/shopify_api/webhooks/request.rb:35-38`) — validation succeeds because the shop header was never part of the signed bytes.
6. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, letting attacker-controlled body content be processed under the victim shop's identity.

### Citations

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
