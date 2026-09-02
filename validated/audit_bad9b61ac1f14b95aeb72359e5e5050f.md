This confirms the finding. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` (which checks the HMAC over `to_signable_string`, i.e. the body) and then dispatches the handler using `request.topic` and `request.shop` taken straight from headers, with no cross-check binding them to the signed body [3](#0-2) .

### Title
Webhook HMAC does not bind the shop/topic headers, allowing cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The gem's inbound webhook verification computes the HMAC exclusively over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `Registry.process` are parsed directly from the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, and `X-Shopify-Api-Version` HTTP headers. None of these headers are covered by the HMAC signature.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field using `OpenSSL.secure_compare` [4](#0-3) . For `ShopifyAPI::Webhooks::Request`, `to_signable_string` is just the raw body string [1](#0-0) . However `shop`, `topic`, and `webhook_id` are all read from headers that are never mixed into the signed payload [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` and, if it passes, dispatches `handler.handle` using `request.shop` and `request.topic` from the headers together with the body: `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [3](#0-2) . There is no code anywhere that binds the verified body to the specific shop/topic headers presented alongside it.

This breaks the identity binding: `hmac == HMAC(secret, body_bytes)` is treated as proof that `shop-domain header == the shop that generated this body`, but the header is never part of the signed bytes, so that equality does not actually hold.

Because every shop installing the same app shares the same app `client_secret`, a legitimate, low-privileged merchant who installs the app on their own store will receive genuine webhooks with valid `X-Shopify-Hmac-Sha256` signatures computed with that shared secret over the body. That merchant can capture one such genuine `(raw_body, hmac)` pair from their own store's webhook traffic, then replay the exact same body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain (and/or a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id` if the body shape is compatible, e.g. an empty `{}` body used by several topics as seen in `test/webhooks/registry_test.rb`). `Utils::HmacValidator.validate` still succeeds because it only checks the body bytes, and the handler is invoked believing the payload originated from the spoofed shop.

### Impact Explanation
This crosses a tenant boundary: an attacker who only has legitimate access to their own shop's installation (no `api_secret_key`, no stolen access token) can cause the app's webhook handler to process attacker-supplied header metadata (`shop`, `topic`, `webhook_id`) as if it were authenticated and originating from a different, victim shop. Any app logic that uses `request.shop`/`WebhookMetadata#shop` to key data writes, cache invalidation, uninstall/redact flows, or authorization decisions can be tricked into acting on behalf of, or against, a shop the attacker does not control — a cross-tenant access issue.

### Likelihood Explanation
Requires only that the attacker (a merchant/installer of the same app) can observe at least one genuine webhook delivery to their own installation, which is trivial to obtain by installing the app and observing traffic to their own endpoint (e.g. via a proxy they control, or an endpoint parameter they influence). No secrets, access tokens, or privileged access to Shopify internals are needed.

### Recommendation
Include the identity-binding headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the signed material verified against the HMAC, or otherwise cryptographically bind them to the body before trusting them (e.g., verify `shop` against a shop known to be associated with a signed value, or require that `webhook_id` be tracked/deduplicated per shop so a captured signature can't be replayed against another shop/topic). At minimum, document that host applications must not trust `WebhookMetadata#shop`/`#topic` without additional shop-scoped validation, since the gem's own HMAC check does not bind them.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Attacker triggers or waits for a webhook (e.g. `orders/create` or a mandatory topic like `customers/redact`, whose body can be `{}` per `test/webhooks/registry_test.rb`) and captures the raw body and the `X-Shopify-Hmac-Sha256` header sent by Shopify — both are signed with the shared app `client_secret`.
3. Attacker replays an HTTP POST to the app's webhook endpoint with:
   - the identical raw body and `X-Shopify-Hmac-Sha256` value captured above,
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`,
   - `X-Shopify-Topic`/`X-Shopify-Webhook-Id` chosen to match a registered handler that accepts the captured body shape.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `to_signable_string` (the body) [5](#0-4) .
5. The registered handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though that shop never sent this webhook, demonstrating cross-tenant spoofing.

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
