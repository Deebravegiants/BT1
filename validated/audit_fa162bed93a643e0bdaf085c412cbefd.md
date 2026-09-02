### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) headers are trusted for tenant attribution but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) used by webhook handlers directly from an HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies only covers the raw request body. This breaks the binding `shop_verified_by_hmac == shop_used_by_handler`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are read straight from caller-supplied headers with no cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates the HMAC using only the body/signature pair, then passes the unverified `shop` header straight to the app's handler as the tenant identifier: [3](#0-2) 

and `HmacValidator.validate`/`validate_signature` confirms this — it only ever signs `verifiable_query.to_signable_string`, which for `Request` is `@raw_body`: [4](#0-3) 

Because the app-level `client_secret` used for HMAC verification is the same across every shop that installs the app, any user who can install the app on their own store (an "unprivileged internet user" from the perspective of any other merchant) can capture a legitimate webhook (valid `raw_body` + valid `hmac`) and replay it to the app's webhook endpoint with the `shopify-shop-domain` header (and/or `shopify-topic`/`shopify-webhook-id`) rewritten to point at a victim shop. `Utils::HmacValidator.validate` still returns true, because the signature only ever covered the body, not the header claiming which shop it came from.

### Impact Explanation
This lets an attacker (with nothing more than their own, legitimately-installed copy of the app) make the app process — and attribute — arbitrary attacker-controlled payloads as belonging to another merchant's shop. Any app logic that keys persistence, authorization, or business actions off `WebhookMetadata#shop` (constructed from this unverified header) will be attacked cross-tenant: data can be written into another shop's records, other-shop state can be mutated, or another shop's install/uninstall/GDPR lifecycle events can be spoofed. This satisfies the "cross-tenant access" Critical impact category from the reproduced identity-binding class ("a field acted on but not covered by the HMAC").

### Likelihood Explanation
Any developer who installs the target app on a store they control can generate arbitrary bodies with valid signatures for that body, and only needs to flip one HTTP header value to misattribute them to a different shop domain — no access to the victim's credentials, tokens, or `client_secret` is required, and no interaction with the host app's business logic beyond the documented `Webhooks::Registry.process` / `Request` API is needed.

### Recommendation
Include the claimed `shop` (and ideally `topic`) in the signable payload/verification step, or independently verify the incoming `shop` header against the set of shops actually installed for this app (e.g., cross-check against an existing offline session for that shop) before dispatching to the handler, rather than trusting the header value once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers any subscribed webhook topic (e.g. `orders/create`) on their own shop, capturing the exact `raw_body` and the `x-shopify-hmac-sha256` value Shopify sent.
3. Attacker POSTs this identical `raw_body` + `hmac` header to the app's webhook endpoint, but rewrites `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) validates successfully because it only checks the body against the secret.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `shop: request.shop` = `"victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

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
