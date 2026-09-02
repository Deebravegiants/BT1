Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id` and `api_version` are all read straight from unsigned HTTP headers [2](#0-1) . `Registry.process` only validates the HMAC of the body via `Utils::HmacValidator.validate(request)` and then hands `request.shop` straight to the handler as the tenant identifier [3](#0-2) .

### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates the HMAC signature over the raw request body only, but exposes `shop` (and `topic`, `webhook_id`, `api_version`) purely from unauthenticated, unsigned HTTP headers. `Registry.process` accepts any request whose body-HMAC is valid, then passes the header-derived `shop` value on to the app's webhook handler as if it were a verified tenant identity.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` against the received `hmac` [4](#0-3) . For webhooks, `to_signable_string` is defined as just `@raw_body` [1](#0-0) . The `shop` accessor, however, is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to the HMAC [5](#0-4) .

`Registry.process` raises only if the body HMAC fails; it does not perform any additional check that the `shop` header is consistent with the payload or with any known session [3](#0-2) . The `shop` value is then forwarded unchanged into `WebhookMetadata`, which is the identity the host application's handler is expected to trust to select which merchant/session/data the webhook applies to.

This is the same class of bug as the H-1 report: a value that drives a security-relevant decision (there, the tax refund amount; here, the tenant/shop identity) is computed from data that is not fully covered by the integrity check (there, `s.share`/`taxFreeAllc` vs. `left`; here, the `shop` header vs. the HMAC-signed body). Concretely, the equality that should hold is:

`shop_bound_by_hmac == shop_used_by_handler`

but the code actually enforces:

`hmac_covers(raw_body) ∧ shop_used_by_handler = header["shop-domain"]` (unbound)

so an attacker who can obtain *any* validly HMAC-signed payload for a topic they subscribed to (e.g., by installing the target app on their own free/dev store and triggering a webhook, since a merchant fully controls the events on their own shop) can replay that exact `raw_body`/`hmac` pair while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop domain. The gem will treat the forged request as authentic and dispatch it to the handler labeled with the victim's shop.

### Impact Explanation
If the host application uses the webhook's `shop` field to look up per-tenant state (access tokens, settings, customer data, GDPR redaction target, etc.) — which is exactly the documented purpose of `WebhookMetadata#shop` — an attacker can impersonate another tenant's webhook stream. This crosses a tenant boundary using only the attacker's own legitimately-issued webhook credentials, i.e., cross-tenant access, without needing the app's `client_secret`, an access token, or any privileged account.

### Likelihood Explanation
Exploitability requires only that the attacker control one shop that has the target app installed and receives webhooks for a topic with attacker-influenceable body content, or simply obtain any raw_body+hmac pair for a topic once, then modify the shop header on replay — both readily achievable by an "unprivileged internet user" running the app on a free development store, without insider access.

### Recommendation
Include the `shop` domain (and ideally `topic`, `webhook_id`, `api_version`) in the signed/verifiable payload used for the HMAC check, or otherwise validate that the shop header is consistent with a value bound to the current app credentials/session before dispatching to handlers — mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in the signed string [6](#0-5) .

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and subscribes to a topic (e.g. `orders/create`) whose body they can fully control (e.g. by creating an order with a chosen payload).
2. Shopify sends the webhook: headers include `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-raw_body>`, plus the raw JSON body.
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value (HMAC is only over body, per `Request#to_signable_string`).
4. Attacker crafts a new HTTP POST to the app's webhook endpoint using the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [7](#0-6) , which succeeds because it only checks the body's HMAC, ignoring the shop header.
6. The handler receives `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim.myshopify.com"` [8](#0-7) , causing the host app to process attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
