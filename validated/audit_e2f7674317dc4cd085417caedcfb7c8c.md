This confirms the root cause: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never mixed into the HMAC computation [2](#0-1) . `Registry.process` only validates `Utils::HmacValidator.validate(request)` (body-vs-signature) and then trusts `request.shop`/`request.topic` to build the `WebhookMetadata` dispatched to the app's handler [3](#0-2) . Since `HmacValidator` signs/verifies only `verifiable_query.to_signable_string` with the single, app-wide `Context.api_secret_key` (shared by every installed shop) [4](#0-3) , the header-level identity fields are unauthenticated relative to that signature.

### Title
Webhook shop/topic identity is not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields used by `Registry.process` to route and label the webhook are taken from HTTP headers that are excluded from the signature. Because the app-level `api_secret_key` (and thus the HMAC) is identical for every merchant shop that installs the app, this breaks the intended binding `hmac-signed-shop == header-shop`.

### Finding Description
`Webhooks::Request#to_signable_string` returns just `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors read `shopify-*`/`x-shopify-*` headers with no cryptographic tie to the HMAC [2](#0-1) . `HmacValidator.validate` recomputes the HMAC purely over `to_signable_string` (i.e., the body) using the shared `Context.api_secret_key` [4](#0-3) , and `Registry.process` treats any request that passes this body check as authoritative for `request.shop`/`request.topic`, dispatching them unchanged to the host app's handler [3](#0-2) .

Because `api_secret_key` is a single per-app secret shared across every merchant's shop (not a per-shop secret), a body+HMAC pair that is valid for shop A's webhook is also a valid body+HMAC pair for the same app's webhook signature check regardless of which shop header accompanies it. The equality the app relies on — "the shop whose HMAC validated" equals "the shop the handler is told the event came from" — does not hold: only the raw body is authenticated, the `shop`/`topic` headers are attacker-controlled bytes layered on top of an otherwise-valid signature.

### Impact Explanation
An unprivileged internet user who has installed the app on their own (attacker-controlled) shop receives legitimate webhook deliveries containing a valid `X-Shopify-Hmac-Sha256` for their own body. Because that HMAC only binds the body, the attacker can replay the exact same raw body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a victim shop. `Registry.process` will accept it as authentic (`HmacValidator.validate` only checks the body) and hand the host application a `WebhookMetadata` claiming to be from the victim shop [5](#0-4) . Any host-app logic that trusts `data.shop` to select tenant state (e.g., to look up a session, mark an order paid, deprovision a shop on `app/uninstalled`, or trigger GDPR redaction on `shop/redact`) is fed forged cross-tenant data — this is a cross-tenant/data-integrity impact stemming directly from this gem's webhook verification contract.

### Likelihood Explanation
Any developer/merchant can self-install the target app to legitimately capture a real, validly-signed webhook body+HMAC for their own shop, then freely replay it with a forged shop header against the app's public webhook endpoint — no access token, `client_secret`, or privileged account is required, satisfying the "unprivileged internet user" bar.

### Recommendation
Bind the identity headers into the signed material: include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise cryptographically bind them, e.g. via a separate per-field HMAC or by requiring the host app to independently confirm `shop` against its own tenant-to-secret mapping) instead of trusting them purely because the body-only HMAC validated. At minimum, document that consumers of `Webhooks::Request#shop`/`#topic` must independently corroborate them (e.g., against a known/expected list of installed shops) before using them for tenant-sensitive actions.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook topic they control (e.g. `products/update`), receiving a POST with headers `X-Shopify-Hmac-Sha256: <H>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: products/update`, and raw body `B`.
2. Attacker resends this exact request to the app's public webhook endpoint but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, keeping body `B` and `X-Shopify-Hmac-Sha256: <H>` unchanged.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `HmacValidator.validate(request)`, which recomputes HMAC over `B` with the shared `api_secret_key` and matches `H` [6](#0-5) .
4. The handler executes with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "products/update", body: parsed_body, ...)` [5](#0-4) , even though the event never originated from Shopify for that shop.

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
