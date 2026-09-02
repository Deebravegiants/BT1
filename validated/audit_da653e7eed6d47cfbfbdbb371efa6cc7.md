Confirmed the root cause. Writing up the finding now.

### Title
Webhook shop/topic identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the value that gets HMAC-verified using only the raw request body [1](#0-0)  while the `shop`, `topic`, `webhook_id`, and `api_version` fields consumed by handlers are read directly from HTTP headers that are never included in that signable string [2](#0-1) . `Registry.process` only validates the HMAC over the body and then trusts `request.shop`/`request.topic` unconditionally to build the metadata passed to the app's handler [3](#0-2) .

### Finding Description
The intended binding is: **the shop that receives credit for a webhook == the shop whose data actually produced the signed body**. Because `to_signable_string` only returns `@raw_body`, and `shop`/`topic`/`webhook_id` are parsed straight from `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id` headers without being covered by the HMAC [4](#0-3) , an attacker who has legitimately received one valid `(body, hmac)` pair for their own shop (e.g., by installing the target app on their own dev/test store and receiving a real webhook delivery) can replay that exact `body` and `hmac` to the app's public webhook endpoint while substituting arbitrary values for `x-shopify-shop-domain` and `x-shopify-webhook-id`. `Utils::HmacValidator.validate` will still succeed because it only recomputes and compares against `to_signable_string` (the body) [5](#0-4) , and `Registry.process` will dispatch the forged `shop` value straight to the registered `WebhookHandler` as authenticated data [3](#0-2) .

The equality that should hold but does not:
`hmac_verified(body) ⇒ shop_header == originating_shop`

is false: the HMAC only proves the body's provenance from *some* installation of the app that shares the same `api_secret_key`, not that the accompanying `shop`/`topic`/`webhook_id` headers originated from that same delivery. Since Shopify's client secret is per-app (shared across every shop that installs the app), any shop that installs a vulnerable app can forge webhook deliveries "from" any other shop of the same app.

### Impact Explanation
This breaks tenant isolation (Critical - cross-tenant access) for any application built on this gem's `Webhooks::Registry`/`WebhookHandler`. A malicious merchant who installs the app can forge webhooks that are processed by the host application as if they came from a different, victim merchant's shop — e.g., forging `shop/redact`, `app/uninstalled`, or order/customer events for a victim `shop-domain`, causing the app to perform cross-tenant actions (data deletion, session invalidation, business-logic side effects) attributed to the wrong tenant, using only a webhook delivery legitimately received on the attacker's own store.

### Likelihood Explanation
Requires the attacker to install the target app on any shop (a normal, unprivileged action any merchant can take) and to have received at least one real webhook delivery — both trivially satisfiable by any customer of the app. No access to `api_secret_key` or any privileged credential is needed beyond what any installer already legitimately receives.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` fields into the HMAC-verified signable string (or otherwise cryptographically bind them, e.g. by including them in the payload signed with the shared secret) instead of trusting the raw headers unconditionally in `Webhooks::Request#to_signable_string`, `#shop`, and `#topic`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, causing the app to register webhooks with the shared `api_secret_key`.
2. Shopify delivers a legitimate webhook to the attacker's endpoint with body `B`, `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the shared secret), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same `B` and `H`, but sends the request with `x-shopify-shop-domain: victim-shop.myshopify.com` (and any desired `x-shopify-topic`, `x-shopify-webhook-id`) to the app's public webhook endpoint.
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because it only checks `B` against `H` [6](#0-5) .
5. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` [7](#0-6) , and the host application acts on the victim's tenant as if Shopify itself sent the event.

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
