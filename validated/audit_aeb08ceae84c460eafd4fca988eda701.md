I have enough evidence to render a determination now.

The root cause is confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `Webhooks::Request#shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header (`lib/shopify_api/webhooks/request.rb:20-23`) without being part of the HMAC-covered signable string. `Utils::HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string`, i.e. body-only (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/utils/verifiable_query.rb:11-15`). `Registry.process` then trusts `request.shop` unauthenticated to build `WebhookMetadata` passed to the merchant's handler (`lib/shopify_api/webhooks/registry.rb:188-199`).

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant shop-attribution spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute exclusively from the `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body (`to_signable_string` returns `@raw_body`). The shop-domain header is therefore not bound to the cryptographic signature at all.

### Finding Description
`Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which recomputes an HMAC over `request.to_signable_string` (the raw body) and compares it to the value carried in the `hmac-sha256` header. It never verifies the `shop-domain` header. After that check passes, `process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` and hands it to the app's handler — the merchant identity (`shop`) delivered to the app's business logic comes from an unauthenticated header.

The identity binding broken is: `HMAC-signed bytes == bytes the app trusts for shop attribution`. In reality:
- HMAC-signed bytes = raw body only.
- Bytes the app trusts for `shop` = the `shop-domain` header, which sits outside the signed payload.

Any party capable of producing a body+HMAC pair that is valid for their own store's webhook (e.g., an attacker who owns a legitimate Shopify store and therefore legitimately receives genuinely-signed webhooks from Shopify for events on that store) can take that valid `(body, hmac)` pair and simply resend it to the target app's webhook endpoint with a different `x-shopify-shop-domain` header. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` will dispatch the attacker-controlled body to the app under the identity of an arbitrary victim shop domain.

### Impact Explanation
This allows cross-tenant data injection/spoofing: an attacker-controlled webhook body (from the attacker's own store, so genuinely signed) can be attributed to any other shop domain the app manages, because the shop identity is never covered by the signature. Depending on how the app's `WebhookHandler` implementations key their data by `WebhookMetadata#shop` (e.g., updating merchant-scoped records, triggering redaction/data flows, feeding order/customer data into per-tenant storage), this breaks tenant isolation, satisfying the "cross-tenant access" Critical impact criterion — data belonging to the attacker's payload gets written/processed under a victim tenant's identity, or conversely used to probe/poison another shop's app state.

### Likelihood Explanation
Likelihood is high for any app that operates multiple shops sharing one webhook endpoint (the typical case for public apps built on this library): the attacker needs no secret material, only a legitimate (even free/dev) store of their own to receive genuinely HMAC-signed webhooks, then replays that body with a modified shop header to the shared endpoint.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header bytes in the signable string used for HMAC validation, or independently verify that the shop-domain header corresponds to a shop the app has an active session for before dispatching to `WebhookHandler#handle`. At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop-domain header so `HmacValidator` binds shop identity to the signature, matching Shopify's actual signing behavior if it does so out-of-band, or explicitly document/enforce that host apps must re-verify `shop` against their own known-shops list before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker registers/owns their own Shopify development store `attacker-shop.myshopify.com`, and the target app is installed there too (or the attacker can trigger a webhook topic on it, e.g. `orders/create`).
2. Shopify sends the app a genuinely signed webhook: body `B`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker intercepts/replays this request to the app's shared webhook endpoint but rewrites the header to `x-shopify-shop-domain: victim-shop.myshopify.com`, keeping body `B` and the same valid HMAC.
4. `HmacValidator.validate` recomputes `HMAC(secret, B)` — matches, since body `B` is unchanged (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) proceeds and calls `handler.handle(data: WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...))`, causing the app to process attacker-supplied body content under the victim shop's identity. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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
