Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers, unauthenticated by the HMAC [2](#0-1) . `Registry.process` validates only the HMAC over the request (i.e., the raw body) and then dispatches the handler using `request.shop` and `request.topic` taken from those same unauthenticated headers [3](#0-2) .

### Title
Webhook shop/topic/webhook_id identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw request body only. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values that `Registry.process` uses to route and label the webhook to a specific tenant/handler are read from HTTP headers that are never included in the signed payload.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `HMAC-SHA256(secret, verifiable_query.to_signable_string)` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled from the `x-shopify-*`/`shopify-*` headers with no cryptographic binding to that signature [2](#0-1) .

`Registry.process` trusts `request.shop` and `request.topic` after confirming only that the body's HMAC is valid: it looks up the handler by `request.topic` and passes `request.shop` into `WebhookMetadata` for the handler to act on [3](#0-2) .

The identity binding that should hold is: `shop authenticated by HMAC == shop the handler acts on`. Because `shop` (and `topic`/`webhook_id`) are excluded from the signed bytes, this equality is not enforced by the gem. An unprivileged internet user who can obtain any one valid `(raw_body, hmac)` pair signed with the app's shared secret — e.g., by registering their own free/dev store on the same app and capturing a real delivery — can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header. `HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will hand the forged shop/topic to the registered handler, which will process attacker-chosen headers as if they were authenticated by Shopify for that shop/topic.

### Impact Explanation
This breaks the binding between the entity Shopify actually authenticated (the raw body content for a specific shop/topic) and the entity the host application acts on (`WebhookMetadata.shop`/`.topic` built from spoofable headers). Depending on how host apps key their per-tenant logic off `WebhookMetadata.shop` (which is the gem's documented API surface for this purpose, see `docs/usage/webhooks.md` and `WebhookMetadata` usage in `lib/shopify_api/webhooks/registry.rb`), this enables cross-tenant data confusion — e.g., causing a handler to apply another shop's webhook body under an attacker-chosen shop domain, or to fire a different topic's handler than the one Shopify actually associated with the delivered payload.

### Likelihood Explanation
The attack does not require the app's `api_secret_key`, an access token, or leaked credentials: it only needs one legitimately-signed webhook body/HMAC pair, which is obtainable by any developer who can install the app on their own store and forward Shopify's own webhook deliveries with modified headers to the target endpoint. Likelihood is moderate — it requires the app to actually key sensitive per-tenant actions off `WebhookMetadata.shop`/`.topic` without independent server-side shop verification, which many integrators using this gem's documented `Registry.process` flow do, since the gem's own webhook contract implies `shop`/`topic` are authenticated.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (in addition to the raw body) in `Webhooks::Request#to_signable_string`, or otherwise require callers to separately compare `request.shop` against the shop associated with the resolved session/tenant before dispatch, so the HMAC binds the full set of fields the handler acts upon.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook delivery with a valid `x-shopify-hmac-sha256` for some `raw_body`.
2. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` and/or a different `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [5](#0-4) .
4. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-controlled `shop`/`topic` values [6](#0-5) , even though the HMAC never authenticated those fields.

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
