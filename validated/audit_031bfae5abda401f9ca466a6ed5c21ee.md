Confirmed: the webhook HMAC signature only covers `@raw_body` via `to_signable_string` [1](#0-0) , while `topic`, `shop`, `api_version`, and `webhook_id` are read straight from HTTP headers that are never included in the signable string [2](#0-1) . `Registry.process` validates only this body-HMAC and then dispatches the handler using the unauthenticated `request.shop`/`request.topic` values [3](#0-2) . `HmacValidator.validate` computes the signature solely over `to_signable_string` (the raw body) with the app's single shared `api_secret_key` [4](#0-3) .

### Title
Webhook tenant identity (`shop`, `topic`) is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying fields `shop`, `topic`, `api_version`, and `webhook_id` directly from unauthenticated HTTP headers, while the HMAC signature verified by `Registry.process` only covers the raw request body. Because the signing secret (`Context.api_secret_key`) is the app's single shared `client_secret` and is identical for every shop that installs the app, a valid `(body, hmac)` pair obtained from any webhook delivery (including one the attacker legitimately receives for their own shop/topic) can be replayed to the same endpoint with a forged `shop-domain`/`topic` header, and the HMAC check will still pass.

### Finding Description
The identity binding that should hold is:
`hmac == HMAC(secret, raw_body)` AND the `shop`/`topic` values acted upon by the handler are cryptographically part of what `hmac` covers.

In this gem, `to_signable_string` returns only `@raw_body` [1](#0-0) , so `shop`, `topic`, `api_version`, and `webhook_id`—all read from the `shopify-*`/`x-shopify-*` headers—are never part of the signed material [2](#0-1) . `Registry.process` validates the HMAC and then trusts `request.shop` and `request.topic` verbatim to route the payload to the registered handler as `WebhookMetadata` [3](#0-2) . Since `Context.api_secret_key` is a single, app-wide secret shared across all merchant shops (not a per-shop key), any two webhook deliveries to the same app produce HMACs computed with the same key. An attacker who legitimately controls a shop (e.g., their own development/partner store) that has this app installed can capture a `(raw_body, hmac)` pair from a real webhook delivery for their own shop and topic, then resend that exact body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` and `shopify-topic` headers to claim they originated from a different shop or different event type. `HmacValidator.validate` will still report the signature as valid because it only checks the body, not the header-derived identity fields [5](#0-4) .

### Impact Explanation
This breaks the tenant boundary the host application relies on: `WebhookMetadata.shop` is the field applications use to attribute the event to a specific merchant record (e.g., to update that shop's data, mark uninstall, etc.). An attacker-controlled shop can cause the handler to process a body under an arbitrary victim shop identity while passing HMAC verification, enabling cross-tenant data manipulation in the host app — a Critical-impact cross-tenant access condition per the rules.

### Likelihood Explanation
Exploitability requires only an unprivileged attacker to have (or create) any shop that installs the target app so they can receive at least one legitimately signed webhook, then replay it with modified identity headers to the same public endpoint. No access to `api_secret_key`, tokens, or privileged accounts is needed beyond what any regular app installer already has.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, and ideally `webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind them to the verified body (e.g., verify against a canonical string containing both body and header values) before trusting `request.shop`/`request.topic` in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and lets it send a legitimate webhook for topic `orders/create` to the app's webhook endpoint; attacker captures the raw body `B` and header `x-shopify-hmac-sha256: H` from this request (HMAC computed with the app's shared `client_secret`).
2. Attacker resends the same body `B` and same header `H` to the same endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` and/or `x-shopify-topic: app/uninstalled`.
3. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares against `H` — this still matches because the secret and body are unchanged [6](#0-5) .
4. The handler is invoked with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim.myshopify.com", body: parsed(B), ...)` [7](#0-6) , causing the host app to act on attacker-supplied data under the victim shop's identity.

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
