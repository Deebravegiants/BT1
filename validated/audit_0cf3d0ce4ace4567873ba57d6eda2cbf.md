### Title
Webhook Shop-Domain Header Is Not HMAC-Bound, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body alone, while `x-shopify-shop-domain` (and topic/webhook-id/api-version) are read from unauthenticated HTTP headers that are never covered by the signature. `Registry.process` validates only the body's HMAC and then dispatches the handler using the unverified `shop` header as the tenant identifier, breaking the equality `shop authenticated by HMAC == shop used as tenant key`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no cryptographic binding to the request: [2](#0-1) 

`HmacValidator.validate` verifies only the `VerifiableQuery#to_signable_string` value (i.e., the raw body) against the app's `Context.api_secret_key`: [3](#0-2) 

`Registry.process` checks that HMAC and then immediately trusts `request.shop` as the tenant identity handed to the app's handler: [4](#0-3) 

Because a webhook's app-level `client_secret` is shared across every shop that installs the app, any merchant who installs the app on their own store (an ordinary, unprivileged action) can capture a fully valid `(raw_body, hmac)` pair for a topic of their choosing. That merchant can then replay the exact same body and HMAC header to the app's webhook endpoint while substituting `x-shopify-shop-domain` for a victim shop. `HmacValidator.validate` still passes because the header is outside the signed content, and `Registry.process` calls `handler.handle(data: WebhookMetadata.new(shop: request.shop, ...))` with the attacker-controlled body attributed to the victim shop: [5](#0-4) 

The gem's own documentation confirms host apps are expected to treat `data.shop` as the authenticated tenant identifier coming out of `Registry.process`, with no additional verification step documented or required: `data` will have "shop, String - The shop domain of the webhook" (see `docs/usage/webhooks.md`).

### Impact Explanation
This breaks the tenant boundary the gem is responsible for establishing: `Registry.process` is the gem's sanctioned way to authenticate that a webhook came from Shopify for a specific shop, but the shop identity is not covered by the same integrity check as the body. An attacker with an unprivileged/self-service app installation on their own store can forge webhooks that the host application will process as if they came from a different merchant's shop, using attacker-controlled body content. This is a cross-tenant access primitive (Critical impact category) achieved purely through this gem's own validation logic, not by relying on the host app ignoring documented behavior — the gem itself hands back an unauthenticated `shop` value as if it were verified.

### Likelihood Explanation
Exploitability only requires: (1) the attacker can install/interact with the target app under their own Shopify store (normal merchant capability, no leaked secrets or privileged access needed), and (2) the ability to POST an HTTP request with custom headers to the app's public webhook endpoint (also unauthenticated/public by design, since Shopify itself must be able to reach it without prior handshake). No access to `api_secret_key`, tokens, or TLS interception is required.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signable payload used by `HmacValidator`, or otherwise cryptographically bind the shop header to the signature before `Registry.process` treats it as an authenticated tenant identifier passed to `WebhookMetadata`. At minimum, document and/or enforce that `request.shop` in `Registry.process` must be cross-checked by the host app against a shop that has an active, registered webhook subscription for that specific `webhook_id`/topic combination before being trusted as a tenant key.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, which shares the same app `client_secret` as every other installation.
2. Attacker triggers a webhook (e.g., `orders/create`) and captures the legitimate raw POST body and its `x-shopify-hmac-sha256` header — this pair is valid per `HmacValidator.validate` because it was truly signed by the app's secret.
3. Attacker resends this exact `(raw_body, hmac)` pair to the app's webhook endpoint, replacing only `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers as usual; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the secret (`request.rb` lines 35-38, `hmac_validator.rb` lines 26-31).
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)` (`registry.rb` lines 198-199), causing the host application to process attacker-controlled data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
