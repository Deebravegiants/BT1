### Title
Webhook shop, topic and API version are unauthenticated header values not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the shop identity (`shop`), event `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers that are excluded from the signed payload. `Webhooks::Registry.process` trusts these header-derived values as the tenant/topic identity forwarded to the app's handler, even though only the body was cryptographically verified.

### Finding Description
`VerifiableQuery#to_signable_string` is the value that `Utils::HmacValidator.validate` HMACs and compares against the `hmac` field [1](#0-0) . For webhooks, `Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is decoded from the `x-shopify-hmac-sha256` header [2](#0-1) ; none of `shop`, `topic`, `api_version`, or `webhook_id` — all read from separate headers — are included in that signable string [3](#0-2) .

`Webhooks::Registry.process` validates only the body/HMAC pair, then looks up the handler using the unauthenticated `request.topic` and forwards the unauthenticated `request.shop` directly to the app's handler as the tenant identity: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

The identity binding this breaks, expressed as an equality that should hold but doesn't:
`hmac == HMAC(secret, raw_body)` is verified, but the code implicitly treats `shop header == shop that produced the signed body` and `topic header == topic that produced the signed body`, which is never checked. The gem's own app-level `api_secret_key` is shared across every shop that installs the app (confirmed by `HmacValidator.validate` using the single `Context.api_secret_key`/`Context.old_api_secret_key`, with no per-shop key) [5](#0-4) , so a valid `(raw_body, hmac)` pair genuinely produced for one shop remains cryptographically valid when replayed with different `shop-domain`/`topic`/`api-version`/`webhook-id` headers.

### Impact Explanation
An unprivileged internet user who can trigger any genuine webhook delivery to the app (e.g., by installing the app on their own store, or performing an action on any shop that has the app installed) obtains a valid `(raw_body, hmac)` pair signed with the app's shared secret. Because the signature covers only the body, that same pair can be replayed to the app's public webhook endpoint with arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-api-version`, and `x-shopify-webhook-id` headers. `Registry.process` will accept it as valid (HMAC check passes) and dispatch it to the handler registered for the forged `topic`, tagged with the forged `shop`. This is a cross-tenant confusion: application logic keyed off `WebhookMetadata#shop`/`#topic` (e.g., updating per-shop state, marking uninstall/orders/GDPR events) can be triggered for a shop the attacker does not control, using data the attacker fully authored. This matches the Critical "cross-tenant access" impact class.

### Likelihood Explanation
The attacker only needs the ability to receive one legitimate webhook from the target app (trivially achieved by installing a public app on a shop they own, or observing any public webhook traffic), and the ability to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is required — the underlying app-level secret used to sign the body is common to all installs, so replay across `shop`/`topic` is straightforward once the attacker has a valid captured body+HMAC.

### Recommendation
Include the tenant/topic identifying values in the signed payload verification path, e.g., have `Webhooks::Request#to_signable_string` (or a dedicated check in `Registry.process`) bind `shop`, `topic`, and `webhook_id` to the verified body — for instance by requiring the app to record/verify the shop-webhook_id pair server-side (idempotency + shop match) rather than trusting the header values outright, and by never dispatching to a handler for a `topic` that wasn't part of what was cryptographically verified.

### Proof of Concept
1. Install the app (or otherwise receive one legitimate webhook) on `attacker-shop.myshopify.com` for topic `orders/create`; capture the raw POST body `B` and its valid `x-shopify-hmac-sha256` header `H` (HMAC of `B` using the app's shared `api_secret_key`).
2. Replay the exact bytes `B` with header `H` unchanged to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: app/uninstalled` (or another registered topic).
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(secret, B) == H`, per `lib/shopify_api/utils/hmac_validator.rb` and `Webhooks::Request#to_signable_string` returning only `@raw_body`.
4. `Registry.process` looks up the handler for the forged `app/uninstalled` topic and invokes it with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "app/uninstalled", body: JSON.parse(B), ...)`, causing the app to act as if the event happened for `victim-shop.myshopify.com`, though it never actually occurred for that shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L189-199)
```ruby
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
