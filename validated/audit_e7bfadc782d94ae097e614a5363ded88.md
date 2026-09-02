## Finding

### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` fields are trusted from unauthenticated HTTP headers while only the raw body is HMAC-covered, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content purely from the raw HTTP body, but exposes `shop`, `topic`, `webhook_id`, and `api_version` as attacker-supplied HTTP headers that are never included in the HMAC digest. `Webhooks::Registry.process` validates only the body's HMAC and then forwards the unauthenticated `shop` header straight to the app's webhook handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from headers, none of which participate in the signature: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it only proves that *some* attacker knows a `(raw_body, hmac)` pair valid for the app's shared `client_secret` — it proves nothing about which header values accompanied that body: [3](#0-2) 

`Registry.process` performs exactly this check and then immediately trusts the unauthenticated `shop` header (along with `topic`/`webhook_id`/`api_version`) as authoritative tenant/event metadata passed to the handler: [4](#0-3) 

Because a single app has one `client_secret` shared across every merchant shop that installs it, any shop owner who has installed the app can legitimately receive a real webhook delivery — i.e. obtain a valid `(raw_body, hmac)` pair signed with the app's secret. That attacker can then resend the exact same body and HMAC to the app's webhook endpoint while swapping the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`webhook-id`) header to claim it originated from a victim shop. The equality the library should enforce — `hmac-authenticated shop == shop acted upon` — is broken: the HMAC only authenticates `raw_body`, while `shop` (the field the handler acts on for tenant-scoped processing) is taken from unauthenticated bytes.

### Impact Explanation
This breaks the tenant boundary between shops sharing the same app installation: an attacker who controls one legitimate shop can present crafted webhook data as another shop's data, since `WebhookMetadata.shop` supplied to the app's handler is not bound to the HMAC-verified payload. This is cross-tenant access delivered through the library's own webhook-processing API (`Registry.process`), not something the host application configures incorrectly — the gem hands the handler an unauthenticated `shop` value while asserting only that "some webhook signed with the app secret" was received.

### Likelihood Explanation
Any user who can install the app on their own Shopify store already possesses a valid `(body, hmac)` pair for the app's `client_secret` via ordinary webhook delivery to their own endpoint; replaying it with a modified `shop-domain` header requires no privileged credentials, TLS interception, or social engineering — only the ability to send an HTTP request to the app's public webhook endpoint.

### Recommendation
Extend the HMAC-covered signable content (or perform a secondary validation step in `Registry.process`) to bind the `shop`, `topic`, `webhook_id`, and `api_version` values to the verified payload, e.g. by requiring the host application to cross-check `request.shop` against the shop associated with the session/subscription that registered the webhook, or by having Shopify sign a canonical string that includes these header values rather than the raw body alone.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a real webhook (e.g. `orders/create`) to the app's endpoint, capturing the raw body `B` and its valid `X-Shopify-Hmac-SHA256` value `H` (both signed with the app's shared `client_secret`).
2. Attacker replays an HTTP request to the same endpoint with the identical body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (line 190 of `registry.rb`, lines 35-38 of `request.rb`).
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` even though the body/HMAC pair was never issued for that shop, and the app's handler processes/acts on data attributed to the victim tenant.

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
