### Title
Webhook `shop`/`topic`/`webhook-id` identity headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop`, `topic`, `api_version` and `webhook_id` values used by `Registry#process` to route and identify the event are taken from unauthenticated HTTP headers. This breaks the binding `hmac-verified bytes == identity claimed for the event`, letting anyone who can produce one valid `(body, hmac)` pair replay it while freely rewriting the tenant identity header.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The HMAC itself is read from the `hmac-sha256` header: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` — the fields that determine *whose* data this webhook is and how it gets dispatched — are pulled straight from other headers that are never part of the signed payload: [3](#0-2) 

`HmacValidator.validate` only checks `hmac` against `to_signable_string` (i.e. the body), so it never validates that the `shop`/`topic`/`webhook_id` headers are consistent with the signature: [4](#0-3) 

`Registry#process` then uses this unauthenticated `request.shop`/`request.topic`/`request.webhook_id` directly as the identity fed to the app's webhook handler after only checking the body HMAC: [5](#0-4) 

This is the exact class of bug named in the rules: "a field acted on but not covered by the HMAC." The equality that should hold is `hmac_verifies(bytes) == identity_of(bytes)`. Here, the HMAC only verifies the request body bytes, while `shop` (the tenant identifier acted on by `Registry#process`/`WebhookMetadata`) comes from a header outside that signed scope. Any actor who can obtain one legitimate `(raw_body, hmac)` pair for their own store's webhook (which is trivial — every merchant/dev who installs their own app on their own shop legitimately receives such webhooks) can replay that exact body+hmac to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value, and the signature check still passes.

### Impact Explanation
If the host application (per the gem's documented API in `docs/usage/webhooks.md`, which routes/persists data keyed by `WebhookMetadata#shop`) uses `shop` to select which tenant's data store to write to, this allows a low-privileged actor who controls only their own shop's webhook traffic to inject data attributed to a different, unrelated shop — a cross-tenant write/confusion. This matches the "cross-tenant access" Critical impact category defined in scope.

### Likelihood Explanation
Likelihood is moderate-to-high for any multi-tenant app: the attacker needs no secret, no privileged account, and no TLS interception — only the ability to trigger a webhook for their own store (something every installer of the app naturally can do) and the ability to POST arbitrary bytes/headers to the app's public webhook endpoint, which is by definition internet-reachable.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed payload used for verification, or otherwise cryptographically bind them to the body (e.g., derive/validate shop identity server-side via a lookup keyed only by a value that is itself covered by the signature) rather than trusting the raw `shopify-shop-domain` header independently of the HMAC check.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and legitimately receives one real webhook: raw body `B` with header `shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared secret) and `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs the same body `B` and same `hmac-sha256` header `H` to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` and `to_signable_string` (=`B`) still match, so `Utils::HmacValidator.validate(request)` in `Registry#process` returns `true`. [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop` is `"victim-shop.myshopify.com"` even though the signed body content belongs to `attacker-shop`, causing the host app to process/store attacker-controlled data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
