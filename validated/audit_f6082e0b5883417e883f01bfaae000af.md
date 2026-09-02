This confirms the identity binding gap: `Webhooks::Request.to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:20-33`) via `shopify_header`. `Registry.process` only calls `Utils::HmacValidator.validate(request)` (`lib/shopify_api/webhooks/registry.rb:189-190`), which recomputes the HMAC over `to_signable_string` (i.e., body only, see `lib/shopify_api/utils/hmac_validator.rb:26-31`) — it never binds the `shop-domain` header into the signed bytes. The `HmacValidator`'s `Context.api_secret_key` is a single per-app secret shared across every installed shop (`lib/shopify_api/context.rb` setup), not a per-shop value, so any shop that has the app installed can obtain validly-HMAC'd webhook bodies.

### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header not covered by HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute exclusively from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` HTTP header, but `to_signable_string` (the bytes that the HMAC actually authenticates) is only the raw request body. Since the HMAC secret is the app's single `client_secret` shared by all installed shops, an attacker who controls one shop with the app installed can capture a genuinely Shopify-signed webhook and replay it to the app's webhook endpoint with the `shop-domain` header swapped to a victim shop, keeping the HMAC valid while `Registry.process` attributes the payload to the wrong tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read from headers that are never part of that signable string: [2](#0-1) 

`Registry.process` validates only the HMAC over that body-only string and then dispatches to the handler using `request.shop` verbatim as the tenant identity: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` recompute the digest purely from `verifiable_query.to_signable_string` (body) and `Context.api_secret_key`: [4](#0-3) 

The broken identity binding, expressed as an equality that should hold but doesn't:
`shop authenticated by HMAC (bytes actually signed = raw_body only)` ≠ `shop used as tenant/session key (request.shop, taken from an unsigned header)`.

Because the `client_secret`/`api_secret_key` used for `HmacValidator` is one value per app (configured once in `ShopifyAPI::Context`), it is identical for every shop that installs the app — it is not a per-shop key. This means a validly-signed webhook body obtained by any one merchant/shop can be replayed against the same endpoint with a different `shop-domain` header value, and the signature check still passes because that header was never part of the signed payload.

### Impact Explanation
This breaks tenant isolation (cross-tenant access): a webhook payload legitimately signed for shop A can be delivered to the host application labeled as shop B by simply changing an HTTP header, with no cryptographic proof binding the shop identity to the signed bytes. Depending on how the host application's `WebhookHandler` uses `WebhookMetadata#shop` (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`, or business-logic webhooks that write/delete data keyed by `shop`), this can let an attacker who controls one installed shop trigger state changes, data exposure, or resource actions scoped to a completely different merchant's tenant — satisfying the "cross-tenant access" Critical impact criterion.

### Likelihood Explanation
Exploitation requires only that the attacker operate (or briefly install the app on) one shop to capture a single genuinely-signed webhook of a given topic/body shape — no `api_secret_key`, access token, or privileged account is required, and no TLS interception is needed since the attacker is the legitimate recipient of their own webhook. Replaying with a modified header is a standard unprivileged HTTP request. The likelihood is bounded mainly by whether the host application's webhook handlers key security-sensitive behavior off `WebhookMetadata#shop` without any additional shop-body cross-check, which is exactly the pattern this gem's own documentation and tests (`test/webhooks/request_test.rb`, `test/webhooks/registry_test.rb`) encourage by exposing `data.shop` directly to handlers.

### Recommendation
Bind the shop identity into the authenticated bytes rather than trusting an unsigned header:
- Extend `Utils::VerifiableQuery`/`Webhooks::Request#to_signable_string` (or a new verification step in `Registry.process`) to require that the shop domain be corroborated from a source covered by the signature — e.g., cross-check `request.shop` against a `shop_id`/`shop_domain` field inside the signed JSON body, when the topic's payload contains one, and reject mismatches.
- At minimum, document prominently that `shop-domain`/`webhook-id`/`topic` headers are **not** covered by HMAC verification and that consuming applications must not treat `WebhookMetadata#shop` as tenant-authenticated without an independent, per-shop check (e.g., confirming the shop exists in the app's own session store before acting).
- Consider deriving/validating the shop from data that is cryptographically tied to the request, consistent with how `JwtPayload` binds `dest`/`aud` for session tokens (`lib/shopify_api/auth/jwt_payload.rb:33-44`).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged Shopify merchant action) and triggers a webhook topic whose body the app processes based on `shop` (e.g. a topic with an empty/static body such as `shop/redact`, or any topic where the body doesn't itself carry the shop domain).
2. Shopify sends the app a request with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid HMAC over raw body>`, and some `raw_body`.
3. Attacker replays that exact HTTP request to the app's webhook endpoint, but changes only the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com` (or `shopify-shop-domain` variant), leaving `raw_body` and `X-Shopify-Hmac-Sha256` untouched.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only (`lib/shopify_api/utils/hmac_validator.rb:26-31`) — this still matches because `raw_body` and the `api_secret_key` are unchanged.
5. `Registry.process` proceeds and invokes the handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now returns `"victim-shop.myshopify.com"` even though the payload was never signed for that shop, causing the host application to perform shop-scoped actions against the victim tenant.

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
