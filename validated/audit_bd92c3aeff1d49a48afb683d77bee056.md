### Title
Webhook shop identity (`X-Shopify-Shop-Domain`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which validates `OpenSSL::HMAC` over `Request#to_signable_string`. For webhooks, that method returns only the raw HTTP body [1](#0-0) , while the `shop` field that the handler subsequently trusts to identify the tenant is read directly from the unauthenticated `X-Shopify-Shop-Domain` header [2](#0-1) . The equality the gem should enforce — "the shop the app acts on" == "the shop bound into the signed bytes" — is broken: the HMAC only binds the body, not the shop-domain header.

### Finding Description
`Registry.process` does:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the value carried in `hmac-sha256` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body` [1](#0-0)  — the `shop`, `topic`, `api_version`, and `webhook_id` headers are excluded from what is signed. `WebhookMetadata`, which is handed to the app's `WebhookHandler#handle`, still carries `shop` taken straight from that unauthenticated header [5](#0-4) , [6](#0-5) .

Because the same `Context.api_secret_key` is shared across all shops that install a given app, any merchant who installs the app (an ordinary, unprivileged action — no leaked credentials or privileged account required) receives real, correctly-HMAC-signed webhooks from Shopify for their own store. That attacker can capture one such `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and, if desired, `webhook-id`/`topic`) for a victim shop. `HmacValidator.validate` still succeeds because it only checks the untouched body bytes against the untouched HMAC; the shop header was never part of the signed input, so tampering with it is undetectable by this gem.

### Impact Explanation
Any host application that uses `request.shop` from `WebhookMetadata` to select which merchant's session/data to operate on (the documented and expected usage pattern — see `docs/usage/webhooks.md` example) will act on behalf of an attacker-chosen shop using a payload the attacker fully controls in relation to that shop. This is a cross-tenant confusion primitive: data intended for the attacker's own shop's webhook can be attributed to, and processed against, a different merchant's tenant context, without the attacker needing that merchant's access token or the app's `client_secret`. This satisfies the "cross-tenant access" bucket.

### Likelihood Explanation
Reaching this requires only: (1) installing the target app on any shop (an unprivileged, self-service action for any Shopify merchant/developer), (2) capturing one legitimately delivered webhook body+HMAC pair from Shopify to that shop, and (3) resending it to the app's webhook route with a different `X-Shopify-Shop-Domain` (and optionally other headers) — all of which are attacker-controlled HTTP request fields that this gem never authenticates. No secret material needs to be derived or brute-forced.

### Recommendation
Bind the tenant/shop identity into the verified signature material for webhooks, e.g., include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (if Shopify's actual signing scheme does not cover them, the gem should independently cross-check `request.shop` against an app-known, previously-registered shop/session before invoking the handler) rather than trusting the raw header value implicitly once body-HMAC validation passes.

### Proof of Concept
1. App A is installed on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` with the app's shared secret), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same `B` and `H` to the same endpoint, changing only `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(secret, B)` and compares to `H` — it matches, since `B` and `H` are untouched: [7](#0-6) .
4. `Registry.process` calls the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)` [6](#0-5) , causing the host app to process attacker-controlled data under the victim shop's tenant context.

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
