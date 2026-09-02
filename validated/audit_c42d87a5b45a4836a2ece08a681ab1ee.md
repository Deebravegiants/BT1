### Title
Webhook shop-domain header trusted for tenant identity without HMAC coverage - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the request body against the HMAC signature, then hands the caller-supplied `shop-domain` header to the app's handler as the trusted tenant identifier, without that header ever being covered by the HMAC.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns only `@raw_body`; none of the headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) are part of the signed material. `HmacValidator.validate` then only proves that `raw_body` was HMAC-signed with `Context.api_secret_key`: [2](#0-1) 

`Registry.process` uses this validation and then forwards `request.shop` (the unauthenticated header value) directly into the handler's metadata: [3](#0-2) 

The identity binding broken: `hmac_valid(body) == true` is treated as equivalent to `shop_header == originating_shop`, but the gem never enforces `HMAC(body, secret) covers shop-domain`. Since the webhook secret (`api_secret_key`) is shared across all shops that install a given app (it's the app's secret, not a per-shop secret), any unprivileged user can install the app on their own development/test store, capture a legitimate `(raw_body, hmac)` pair delivered to their own webhook endpoint, and replay that exact body+HMAC to the host application's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop). `Registry.process` will pass HMAC validation (since the body/HMAC pair is genuinely valid) and will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop, even though the actual event, if any, originated from the attacker's own store.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker-controlled request can cause the host application's webhook handler to act as though a payload originated from a different (victim) shop, because the gem exposes an unauthenticated `shop` field to the handler despite validating the request via HMAC. Any app relying on `WebhookMetadata#shop` (populated at `lib/shopify_api/webhooks/registry.rb:198`) to select the tenant/session context for processing the payload is exposed to cross-tenant data confusion or forced actions attributed to the wrong shop.

### Likelihood Explanation
Requires only that the attacker has (or can obtain, e.g., by installing the target app on their own store, which any unprivileged internet user can generally do for public apps) a valid `(raw_body, hmac)` pair — no access to `api_secret_key` itself is needed, since the pair is exactly what Shopify's own delivery would send to any installed shop's configured endpoint. The forged `shop-domain` header is trivially attacker-controlled since it is never covered by the signature.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`api-version`/`webhook-id`) header values into the signed material verified by `HmacValidator`, or otherwise cryptographically bind the shop identity to the payload before exposing it via `WebhookMetadata`. At minimum, document/require that consuming applications must independently re-verify that the shop domain in a webhook request matches a shop with a known active installation before trusting it for any tenant-scoped action, since this gem does not perform that binding itself.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, receiving a real webhook delivery with a genuinely valid `x-shopify-hmac-sha256` header for the `raw_body` (which may be empty/generic content, e.g., `{}` or a topic with a body independent of shop identity).
2. Attacker replays the identical `raw_body` and `x-shopify-hmac-sha256` value to the host application's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body successfully; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the HMAC — this passes.
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, even though the shop header was never covered by the signature, per [4](#0-3) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
