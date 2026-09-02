### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by the HMAC signature, allowing cross-tenant metadata spoofing on replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content solely from the raw HTTP body [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only that the body's HMAC is correct, then forwards these header-derived, unsigned values to the app's handler as trusted identity data [3](#0-2) .

### Finding Description
The binding that should hold is: `shop_bound_by_hmac == shop_delivered_to_handler`. In `Request#to_signable_string`, only `@raw_body` is fed into the HMAC computation [1](#0-0) . The `shop` value used to build `WebhookMetadata` comes from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed material [4](#0-3) . Same for `topic` and `webhook_id` [2](#0-1) .

`Registry.process` performs `Utils::HmacValidator.validate(request)` [5](#0-4) , which calls `HmacValidator.validate_signature`, comparing the HMAC of `to_signable_string` (i.e., of the body only) against the received signature [6](#0-5) . Once that body-only check passes, the code trusts `request.shop`, `request.topic`, `request.webhook_id` unconditionally and passes them into `WebhookMetadata`, which is delivered to the app-defined `handler.handle` [7](#0-6) [8](#0-7) .

This mirrors the report's root cause pattern: a value is trusted as an identity key (the token/shop) without verifying it is bound to the authenticated channel (the balance delta/HMAC signature), letting an attacker present the same authenticated payload under a different identity label.

### Impact Explanation
An attacker who legitimately receives (or can trigger) any real webhook delivery for their own installed shop obtains a genuinely-signed `(raw_body, hmac)` pair. Because the HMAC never covers the `shop-domain` header, the attacker can replay that exact body+signature to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header value. `HmacValidator.validate` still returns true (body and signature match), and the registry hands the handler a `WebhookMetadata` whose `shop` field is the attacker-chosen victim domain [7](#0-6) . Any handler that keys storage, session invalidation, billing, or business logic off `data.shop` (the gem's own `WebhookMetadata.shop` field exists specifically to be used this way) can be tricked into acting on the wrong tenant — e.g., firing an `app/uninstalled`-style handler for a shop that never sent it, or writing attacker-controlled body content under another merchant's shop record. This is a cross-tenant impact reachable purely by an unprivileged webhook sender who possesses one valid signed payload of their own.

### Likelihood Explanation
Moderate-to-high: no access token, `client_secret`, or credential leak is required — only replay of a webhook the attacker legitimately received for their own shop, with a modified header field that this library never authenticates. This is consistent with Shopify's documented webhook signing scheme (HMAC over body only), so the gap is not host-application misuse of a documented API contract — it's this library exposing header-derived `shop`/`topic`/`webhook_id` as if they were verified identity fields.

### Recommendation
Do not treat `Request#shop`, `#topic`, `#webhook_id`, or `#api_version` as authenticated. At minimum:
- Document explicitly that these header values are unauthenticated and must not be used as a sole tenant/session key without corroboration from the signed body (many webhook payloads include the shop id/domain in the body).
- Where feasible, cross-check the header `shop` against an authoritative shop identifier embedded in the parsed body before constructing `WebhookMetadata`, or extend `to_signable_string`/verification to bind the headers used for routing to the signature check.

### Proof of Concept
1. App using this gem registers a webhook handler that keys off `WebhookMetadata#shop` (as documented in `docs/usage/webhooks.md`) to store or act on shop-scoped data.
2. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery, capturing the raw body and its valid `X-Shopify-Hmac-SHA256` value.
3. Attacker resends this exact `(raw_body, hmac)` pair to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the signature only verifies `raw_body` [5](#0-4) [9](#0-8) .
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` and passed to the app handler [7](#0-6) , causing the handler to perform its logic against the victim tenant using attacker-supplied body content.

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
