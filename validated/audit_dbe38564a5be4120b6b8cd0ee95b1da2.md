### Title
Webhook `shop`, `topic`, and `webhook-id` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements the `VerifiableQuery` interface but its `to_signable_string` returns only `@raw_body`, excluding the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers from the HMAC-signed payload. Because the app's `api_secret_key` is a single shared secret across every shop that installs the app (not a per-shop secret), any shop owner who has the app installed can obtain a genuinely Shopify-signed `(body, hmac)` pair for their own store's webhook, then replay that exact pair against the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `topic`, `webhook-id`) header to point at a different, victim shop. `HmacValidator.validate` only checks the body against the secret and will accept the forged request, letting `Webhooks::Registry.process` dispatch attacker-controlled data tagged as belonging to another tenant.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

which only signs `@raw_body`, while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated headers: [2](#0-1) 

`HmacValidator.validate` verifies the received HMAC against `to_signable_string` only: [3](#0-2) 

`Webhooks::Registry.process` then uses the unauthenticated `request.shop` and `request.topic` to build the tenant/topic context handed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop header == shop whose data actually produced/authorized this signed body`. Before the attacker's request: a webhook body `B` with HMAC `H = HMAC(secret, B)` is delivered by Shopify with headers correctly identifying shop `S1`, and `H` validates. After the attacker's request: the same `(B, H)` pair is replayed with the `shop-domain` header rewritten to `S2` (a different shop using the same app). `HmacValidator.validate` still returns `true` because it recomputes `HMAC(secret, B)` and compares it to `H` — it never looks at the `shop-domain`, `topic`, or `webhook-id` headers. `Registry.process` therefore calls the handler with `WebhookMetadata(shop: "S2", topic: request.topic, body: parsed B, ...)`, even though `B` was never signed in association with `S2`. The equality `authenticated_shop == attributed_shop` is broken: the HMAC only proves "some install of this app produced this body," not "shop S2 produced this body."

### Impact Explanation
This breaks the tenant identity binding at the core of webhook processing: the gem lets any shop that has legitimately installed the app forge webhook deliveries that are processed as if they originated from an arbitrary other shop on the same app, without needing `api_secret_key`, an access token, or any elevated privilege — only a normal, unprivileged merchant/app-install account and the ability to POST to the app's public webhook endpoint. Depending on how the host application keys data by `WebhookMetadata#shop` (order sync, inventory updates, customer data ingestion, etc.), this enables cross-tenant data injection/corruption, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is moderate-to-high in any multi-tenant app: the attacker needs only (1) their own shop's install of the app (unprivileged, self-service), (2) one legitimately delivered webhook to capture a valid `(body, hmac)` pair, and (3) the ability to send an HTTP POST with modified headers to the app's public webhook URL — all of which are available to a standard, unprivileged internet user/merchant with no secret material.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed payload used by `Request#to_signable_string`, or otherwise cryptographically bind them to the verified body (e.g., compute the signature over a canonical concatenation of headers + body, matching how Shopify itself should sign, or reject/ignore any header not certified) before they are exposed via `WebhookMetadata` to the host application's handler.

### Proof of Concept
1. App installs on shop `S1`; Shopify delivers a webhook with body `B`, headers including `x-shopify-shop-domain: S1.myshopify.com`, `x-shopify-hmac-sha256: H` where `H = base64(HMAC-SHA256(secret, B))`.
2. Attacker (owner of `S1`, unprivileged w.r.t. the app/host) captures this raw request (e.g., via their own request logs/proxy on their own store's webhook receiver, or a shared receiving endpoint).
3. Attacker resends the exact same body `B` and `hmac-sha256` header `H` to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `S2.myshopify.com` (a different shop using the same app).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: S2...})` is constructed; `Utils::HmacValidator.validate(request)` calls `to_signable_string` → returns `B` only, recomputes `HMAC(secret, B) == H` → validation passes.
5. `Webhooks::Registry.process` invokes the handler with `WebhookMetadata.new(topic: request.topic, shop: "S2.myshopify.com", body: parsed(B), ...)` — the host application now processes attacker-supplied data attributed to shop `S2`, despite it never being signed for `S2`.

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
