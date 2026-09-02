## Title
Webhook `shop` (and `topic`/`webhook_id`) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then trusts the `shop`, `topic`, and `webhook_id` values taken directly from HTTP headers — none of which are covered by that HMAC. Because a single shared `api_secret_key` (the app's client secret) is used to sign webhooks for every shop that installs the app, any merchant who has installed the app can capture a legitimately-signed `(raw_body, hmac)` pair delivered to their own endpoint and replay it with a forged `shopify-shop-domain` header, causing the app to process attacker-supplied webhook data under a victim shop's identity.

### Finding Description
The HMAC validation only signs the raw body: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read straight from headers and are excluded from `to_signable_string`: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC — it never verifies that the `shop` header matches the tenant the body actually originated from: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` header value, passing it straight to the app's handler as the tenant identity: [4](#0-3) 

The equality this breaks is:

`shop authenticated by HMAC (none — HMAC covers only raw_body)` ≠ `shop trusted as the tenant key for handler dispatch (request.shop, an unauthenticated header)`

Since Shopify signs webhooks for every shop that installs a given app using that app's single `client_secret` (the gem's `Context.api_secret_key`), any unprivileged internet user who installs the app on their own store receives a validly-signed `(raw_body, hmac)` pair. Because the header set (`shop`, `topic`, `webhook_id`, `api-version`) is entirely outside the signed bytes, that same attacker can replay the identical body/HMAC to the app's webhook endpoint while substituting a different `shopify-shop-domain` header value. `Registry.process` will accept the HMAC as valid (it only checks the body) and dispatch the (attacker-controlled) body to the handler tagged with an arbitrary `shop` value of the attacker's choosing.

### Impact Explanation
This breaks the tenant boundary the webhook processing pipeline is meant to enforce: an app relying on `WebhookMetadata#shop` (as documented in `docs/usage/webhooks.md`, `data.shop`) to scope which merchant's records to create/update will process forged data under another shop's identity. This is a cross-tenant integrity/confusion issue — a low-privilege actor (any developer/merchant who can install the target app) can inject fabricated webhook events attributed to a shop they do not control.

### Likelihood Explanation
Any entity that can install the app (a normal, unprivileged step — no access token, no leaked credentials, no `api_secret_key` knowledge required) can obtain a real signed webhook. Replaying it with a modified `shop-domain` header requires only basic HTTP tooling; no cryptographic secret needs to be recovered because the header is simply never part of what's signed.

### Recommendation
Bind the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api-version`) into the signable material verified by the HMAC, or otherwise cryptographically bind the shop the HMAC/secret pertains to before trusting `request.shop` for dispatch. At minimum, `Registry.process` should not treat `request.shop` as trusted tenant context based solely on a body-only HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook: body `B`, headers include `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same `B` and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` — this only recomputes the HMAC over `B`, which still matches. See: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and body `B`, even though `B` was never generated for `victim.myshopify.com`.

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
