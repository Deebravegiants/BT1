## Analysis

The gem's webhook-processing path breaks exactly the identity binding called out in scope: *"a shop authenticated versus the shop stored as a session key"* / *"a field acted on but not covered by the HMAC."*

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0)  while `shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, completely outside the signed payload [2](#0-1) . `Registry.process` validates only the body's HMAC and then forwards the unverified `shop` header straight into `WebhookMetadata` that the host app trusts as the tenant identifier [3](#0-2) , and `WebhookMetadata#shop` is declared as a plain trusted `String` field [4](#0-3) .

By contrast, the OAuth `AuthQuery` used for the callback HMAC *does* include `shop` inside `to_signable_string`, so it is bound to the signature [5](#0-4) . This shows the library's own convention treats `shop` as something that should be covered by the signature — the webhook path simply omits it.

Because `Context.api_secret_key` (the app's `client_secret`) is a single shared secret across every shop that installs the app [6](#0-5) , any merchant who legitimately installs the app can obtain a `(body, hmac)` pair that is valid under that shared secret (e.g. from a real webhook delivered to their own shop, or by triggering any webhook-eligible event in their own store). Because `shop` is never part of the signed content, that same `(body, hmac)` pair remains valid if replayed to the app's webhook endpoint with an arbitrary, attacker-chosen `x-shopify-shop-domain` header. `HmacValidator.validate` will pass, and `Registry.process` will hand the host app a `WebhookMetadata` claiming the payload belongs to a victim shop chosen by the attacker [3](#0-2) .

### Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` value that the library forwards to the host application as the authoritative tenant identifier is read from an unauthenticated HTTP header. Because the webhook-signing secret (`Context.api_secret_key`, the app's `client_secret`) is shared across all shops that install the app, an attacker who has any valid `(body, hmac)` pair for their own shop can replay it with a different `shop-domain` header and have it accepted as coming from an arbitrary victim shop.

### Finding Description
`to_signable_string` in `lib/shopify_api/webhooks/request.rb` returns `@raw_body` alone [1](#0-0) . The `shop` accessor reads directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to the HMAC [2](#0-1) . `Utils::HmacValidator.validate` only checks that the supplied `hmac` matches a signature computed from `to_signable_string` (the body) [7](#0-6) , so the `shop` header can be freely altered post-signing without invalidating the HMAC check. `Registry.process` then trusts this unverified header value and passes it into `WebhookMetadata`, which is delivered to the application's webhook handler as the tenant the payload belongs to [3](#0-2) .

This is the same class of bug as the reported issue: a value that is acted upon downstream (`shop`, used exactly like the drained "value" in the report) is never included in the integrity check (the HMAC/compliance validation), so a party with a validly-signed message for one context can redirect its effect into another context. The library's own `AuthQuery` demonstrates that `shop` is intended to be a signed field — it explicitly includes `shop` in its `to_signable_string` for the OAuth callback HMAC — while the webhook `Request` path silently omits it [5](#0-4) .

### Impact Explanation
Since `Context.api_secret_key` is the single `client_secret` shared by the app across every merchant installation [6](#0-5) , any installed merchant (an unprivileged, low-trust actor relative to other tenants) can obtain a validly-HMAC-signed body for a webhook belonging to their own shop, then replay that exact body with a forged `shop-domain` header naming a different, victim shop. The application receives `WebhookMetadata.shop` pointing at the victim tenant while `HmacValidator.validate` reports success, causing the app to process/store attacker-controlled data under another tenant's identity — a cross-tenant integrity violation.

### Likelihood Explanation
Exploitation only requires (1) installing the app as a normal merchant to legitimately receive at least one signed webhook body, and (2) sending an HTTP POST to the app's public webhook endpoint with that body/HMAC pair and an arbitrary `shop-domain` header — no access token, `client_secret`, or privileged credentials are needed. This is reachable by any unprivileged internet user who can install the app once.

### Recommendation
Bind `shop` (and other identity-relevant fields such as `topic`) into the HMAC-signable content for webhooks, mirroring `AuthQuery`'s approach, or otherwise cryptographically verify that the `shop-domain` header matches the shop implied by the signed body/topic before constructing `WebhookMetadata`. At minimum, document that host applications must independently re-derive/verify the shop for each webhook rather than trusting `WebhookMetadata#shop` as authenticated.

### Proof of Concept
1. App has `client_secret` `S`, shared across all installs.
2. Attacker installs the app on `attacker-shop.myshopify.com`, triggers any event, and captures the resulting webhook POST: body `B`, header `x-shopify-hmac-sha256: HMAC(B, S)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker sends a new POST to the app's webhook endpoint with the identical body `B` and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/webhooks/registry.rb` (line 190) succeeds because it only checks `B` against the HMAC. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and invokes the app's handler, which acts on attacker-controlled data as though it originated from `victim-shop`.

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
