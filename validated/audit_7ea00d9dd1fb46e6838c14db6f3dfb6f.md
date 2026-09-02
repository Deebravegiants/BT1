This confirms the vulnerability. The `Webhooks::Request#to_signable_string` only returns `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from unauthenticated HTTP headers [2](#0-1) . `HmacValidator.validate` only checks that the raw body matches the secret-derived signature [3](#0-2) , so it never binds the `shop-domain`/`topic` headers to that signature. `Registry.process` then trusts `request.shop` and `request.topic` directly to dispatch the webhook to the app's handler [4](#0-3) .

### Title
Webhook shop/topic identity not bound to HMAC signature allows cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop-domain` and `topic` headers used to route and process the webhook are never covered by that signature. Any party who can obtain one validly-signed webhook body (e.g., a merchant installing the app on their own store) can replay that exact body to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header pointing at a different shop, and `HmacValidator.validate` will still accept it because it only checks `raw_body` against the signature.

### Finding Description
The equality that should hold is: `shop authenticated by HMAC == shop the handler acts on`. Instead:
- `to_signable_string` returns only `@raw_body` [1](#0-0) .
- `shop`, `topic`, `webhook_id`, `api_version` are read straight from attacker-controllable HTTP headers, with no cryptographic binding to the signed payload [2](#0-1) .
- `HmacValidator.validate_signature` recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac` header value, with no reference to shop/topic [3](#0-2) .
- `Registry.process` validates the HMAC, then unconditionally trusts `request.topic` and `request.shop` to look up the handler and construct `WebhookMetadata` passed to the app's business logic [4](#0-3) .

Because a single app installation uses one shared `client_secret` across all shops that install it, any merchant who installs the app can receive legitimately-signed webhooks for their own shop. The signature over the body does not encode which shop or topic it belongs to, so that same signed body/HMAC pair can be re-submitted with a different `shop-domain` (or `topic`) header and will pass `HmacValidator.validate` unchanged, letting the attacker's traffic be attributed to a victim shop inside the app.

### Impact Explanation
This is a cross-tenant integrity violation: an unprivileged merchant (one who has legitimately installed the app, i.e., an "unprivileged internet user" relative to other tenants of the same app) can inject forged webhook events attributed to another shop. Depending on how the host app's `WebhookHandler` implementations use `shop`/`topic` (e.g., `app/uninstalled` cleanup, `customers/redact`, order/customer state changes), this can trigger destructive or data-corrupting actions against a victim tenant's data/session without their knowledge — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: exploitation requires only that the attacker be able to install the target app on any store (a normal, unprivileged action), capture one webhook delivery to their own endpoint, and replay it with modified headers. No secrets, tokens, or privileged access are needed beyond becoming a regular merchant user of the app.

### Recommendation
Bind the shop/topic identity to the HMAC-verified payload instead of trusting side-channel headers independently. Options: verify that `request.shop` and `request.topic` are consistent with values embedded/echoed in the signed body where Shopify provides them, or, at minimum, document/require that `to_signable_string` (or an additional check) incorporate the shop-domain and topic headers into the value verified against the secret, matching Shopify's own webhook verification guidance which only guarantees payload integrity — the host application must independently ensure the shop header corresponds to a shop it has an active session/install record for before acting on the payload, and this gem should surface that requirement rather than implicitly trusting `request.shop`.

### Proof of Concept
1. Install the target app on `attacker.myshopify.com`; trigger any webhook topic (e.g., `orders/create`) to receive body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (signed with the app's `client_secret` over `B`).
2. Resend the same `raw_body: B` with the same `hmac-sha256` header `H`, but replace `X-Shopify-Shop-Domain` with `victim.myshopify.com` (and optionally a different `X-Shopify-Topic`) when constructing `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)`.
3. Call `ShopifyAPI::Webhooks::Registry.process(request)`; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `H` [5](#0-4) , and the handler is invoked with `shop: "victim.myshopify.com"` [6](#0-5) , processing attacker-controlled data as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
