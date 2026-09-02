### Title
Webhook `shop` and `topic` identity are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC exclusively against this signable string (the body), so the `shop`/`topic` values used by `Registry.process` to route and stamp webhook data are never bound to the signature that is checked.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` by defining: [1](#0-0) 
which only returns `@raw_body`. Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from caller-supplied headers with no cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the HMAC purely from `to_signable_string` (i.e., the body) and compares it against the received `hmac` header: [3](#0-2) 

`Registry.process` trusts `request.shop` and `request.topic` directly to build the data handed to the app's handler, after only checking the body HMAC: [4](#0-3) 

The binding that should hold is:
`hmac_verified(shop, topic, body) == true` for the `(shop, topic, body)` triple actually processed.

What actually holds is:
`hmac_verified(body) == true`, while `shop` and `topic` are taken from the headers unconditionally, i.e. `shop_used_by_handler != shop_covered_by_hmac` (the latter set is empty).

Since the app's `client_secret` (the HMAC key) is shared across every shop that has the app installed, any user who has installed the app on their own shop can obtain a body + valid HMAC pair from a webhook Shopify legitimately sent to their store. They can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for a different shop domain. `HmacValidator.validate` still returns `true` because it never looked at those headers, and `Registry.process` forwards the forged `shop`/`topic` to the handler as if it were authentic.

### Impact Explanation
This breaks the identity binding between the merchant/shop that legitimately generated a webhook and the shop the host application believes sent it, enabling a single-app-install attacker to inject data attributed to another tenant. Depending on how the host app's webhook handler uses `shop`/`topic` (e.g., writing to shop-scoped data stores, updating billing/subscription state, or triggering shop-specific actions), this can result in cross-tenant data corruption or unauthorized actions performed against a victim shop's tenant — matching the "cross-tenant access" Critical impact category, since the app can be tricked into mixing data across tenants without ever compromising the victim's own credentials.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the app on any single shop (a normal, low-privilege action available to any Shopify merchant/developer) and be able to send arbitrary HTTP requests to the app's public webhook endpoint — both are trivially available to an "unprivileged internet user" relative to the victim's tenant. No access token, `api_secret_key`, or victim credentials are needed.

### Recommendation
Include `shop` and `topic` (and any other header fields the handler trusts) inside the HMAC-covered payload, or independently verify that the `shop-domain`/`topic` headers correspond to the shop/topic the app expects for that specific webhook subscription (e.g., cross-check against the shop that owns the record being acted upon before trusting the header value). At minimum, `to_signable_string` should incorporate the header values that downstream code relies upon for identity/authorization decisions, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`/`state`/etc. into its signable string.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared `client_secret`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com` (and/or `x-shopify-topic` to a different registered topic).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic: "victim-facing topic", shop: "victim.myshopify.com", body: parsed(B), ...)` and performs actions/data writes scoped to `victim.myshopify.com` using attacker-controlled body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
