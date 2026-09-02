This confirms the finding: `Webhooks::Request#to_signable_string` returns only `@raw_body`, meaning the HMAC (which is computed with the app's `api_secret_key`, per `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb`) only authenticates the body bytes. The `shop`, `topic`, `api_version`, and `webhook_id` fields are all read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) and are never included in the signed payload. `Registry.process` then trusts `request.shop` and forwards it unauthenticated into `WebhookMetadata`, which application webhook handlers use to determine which tenant/shop record to act on. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) Headers Are Not Covered by the HMAC Signature, Allowing Cross-Tenant Shop Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC digest only over the raw request body (`to_signable_string` returns `@raw_body`), while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers that are never part of the signed content. `Registry.process` validates only the body-bound HMAC and then blindly trusts the header-derived `shop` value when constructing `WebhookMetadata` passed to the app's webhook handler. This breaks the identity binding: `shop` used-by-handler ≠ `shop` covered-by-HMAC.

### Finding Description
`HmacValidator.validate` recomputes an HMAC-SHA256 over `verifiable_query.to_signable_string` using `Context.api_secret_key` and compares it to the `hmac` field via `OpenSSL.secure_compare`. For `Webhooks::Request`, `to_signable_string` is simply `@raw_body` — the raw JSON body bytes. [4](#0-3) 

However, `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` HTTP headers, none of which are included in `to_signable_string`: [5](#0-4) 

`Registry.process` verifies the HMAC and then unconditionally uses `request.shop` (a header value that was never authenticated) to build the `WebhookMetadata` object dispatched to the app's handler: [6](#0-5) 

Because the same body+HMAC pair remains valid regardless of which `shop-domain` header accompanies it, an attacker who can capture (or otherwise obtain) one valid `(raw_body, hmac)` pair for a given app — e.g. from a webhook delivered to their own controlled shop after installing the app, or from any endpoint/log that leaks a legitimate webhook delivery — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still report the request as valid, since it never inspects the header, and the handler will process the payload as if it originated from the spoofed shop.

This directly matches the bug class in the report: a value acted upon downstream (the `shop` used to select the affected tenant/session) is not the value protected by the integrity check (the HMAC only binds the body), so the two "identities" — HMAC-authenticated shop vs. handler-trusted shop — are never proven equal.

### Impact Explanation
Any application that uses `request.shop` (or `WebhookMetadata#shop`) to look up/update per-tenant records — e.g. deleting data for `customers/redact` or `shop/redact`, updating order/inventory state, or deactivating a shop's session — can be made to apply a legitimate, HMAC-valid webhook body against an attacker-chosen shop identifier, since the HMAC gives no guarantee about which shop the body belongs to. This is a cross-tenant integrity issue: it lets an unprivileged party who merely installs the app on their own shop (thus receiving genuine signed webhook bodies) redirect those bodies' processing effects onto a different merchant's tenant by spoofing only the unauthenticated `shopify-shop-domain` header.

### Likelihood Explanation
Any party who can install the app on a shop they control receives real webhook deliveries (raw body + valid HMAC, signed with the app's own `api_secret_key`) for that shop. Reusing that exact `(raw_body, hmac)` pair while swapping only the `shopify-shop-domain` header (and, if desired, `webhook-id`/`topic`) is a header-substitution replay requiring no cryptographic material and no privileged access — it only requires the gem's own `Registry.process`/`HmacValidator.validate` logic, which never checks the header against the signed content.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signable content (or otherwise cryptographically bind them, e.g. incorporate the headers into the digest input), so that tampering with any of these headers invalidates the HMAC. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should include the shop-domain header value alongside the raw body, and `Registry.process` should reject requests where the header-derived shop is not provably tied to the signed payload.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; Shopify delivers a legitimate webhook (e.g. `orders/create`) to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and body `B`.
2. Attacker (who controls the receiving endpoint or intercepts the delivery) captures `B` and the valid `hmac`.
3. Attacker resends the exact same `B` and `hmac` to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) only — it never sees or validates the `shop-domain` header, so validation succeeds.
5. `handler.handle` is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process `B`'s effects (e.g. a redact/update action) against `victim-shop.myshopify.com` instead of the shop that actually generated the webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
