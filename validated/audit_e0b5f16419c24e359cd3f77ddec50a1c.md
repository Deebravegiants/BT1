### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers. Any user who can obtain one genuine `(body, hmac)` pair for the app (e.g., by installing a public app on their own shop and receiving a real webhook) can replay that exact body/hmac pair while forging the shop-domain, topic, or webhook-id headers to any value. `Utils::HmacValidator.validate` only checks the body bytes, so the forged headers pass validation, and `Registry.process` hands the forged `shop`/`topic`/`webhook_id` straight to the app's handler as trusted metadata — breaking the binding "shop authenticated == shop the app stores as the tenant key."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled directly from headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then dispatches using the unauthenticated `topic`/`shop` values as trusted tenant/routing identifiers: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm the check is scoped strictly to `to_signable_string` (the raw body), never the headers: [4](#0-3) 

Because the same `client_secret`-derived HMAC key is shared across every shop that has an app installed, an unprivileged attacker who installs the public app on their own shop will receive a legitimately-signed `(raw_body, hmac)` pair from Shopify. Since the header fields are outside the signed content, the attacker can replay that exact body+hmac to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (a victim shop), `x-shopify-topic`, or `x-shopify-webhook-id`. `HmacValidator.validate` still returns `true` because it only checks the raw body against the secret, and `Registry.process` forwards the forged `shop`/`topic` to the handler as `WebhookMetadata`, which apps commonly use as the tenant key to route/store data.

### Impact Explanation
This breaks the identity binding "the shop verified via HMAC == the shop the app records/stores against," letting a low-privileged attacker (any merchant able to install the app once) inject data or trigger business logic under a victim shop's identity — a cross-tenant access vector matching the Critical bar for "cross-tenant access" in this gem's threat model.

### Likelihood Explanation
Likelihood is high for any public/multi-tenant app relying on this gem's `Webhooks::Registry`/`Request`: the only prerequisite is a genuine webhook delivery to the attacker's own shop (trivial via a free/dev install), after which the header forgery and replay require no secret knowledge.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the HMAC-signable content, or otherwise cryptographically bind these header values to the signed body before trusting them as tenant/routing identifiers in `Registry.process`.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` and triggers a real event (e.g., `orders/create`), capturing the resulting webhook `raw_body` and its valid `x-shopify-hmac-sha256` header from Shopify.
2. Attacker replays the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic` to a topic of choice.
3. `Utils::HmacValidator.validate` passes (body/hmac match), `Registry.process` dispatches to the registered handler with `shop: "victim-shop.myshopify.com"`, and the app processes attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
