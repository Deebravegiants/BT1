## Title
Webhook `shop` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing — (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content from the raw body only, while the `shop`, `topic`, and `webhook_id` used to route and attribute the webhook are read straight from unauthenticated HTTP headers. `Registry.process` accepts the request as valid as long as `Utils::HmacValidator.validate(request)` succeeds against the raw body, then hands `request.shop` (and the other header-derived fields) to the app's handler without any cross-check that this shop is the one that actually produced the signed body. This breaks the intended identity binding `shop that authenticates the payload == shop attributed to the payload by the handler`.

### Finding Description
`to_signable_string` for a webhook request returns only the raw body: [1](#0-0) 

But `shop`, `topic`, and `webhook_id` are pulled directly from headers with no relationship to the signed bytes: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts the header-derived `shop` for dispatch to the handler: [3](#0-2) 

`HmacValidator.validate` computes the signature with the single, app-wide `Context.api_secret_key` (the same secret is used for every shop that has this app installed): [4](#0-3) 

Because the HMAC is scoped only to the body and keyed by a secret shared across all tenants of the app, any merchant who has legitimately installed the app (an "unprivileged" actor relative to *other* tenants) receives real webhook deliveries at their own endpoint and can observe a valid `(raw_body, X-Shopify-Hmac-Sha256)` pair for that app. Nothing in this gem prevents that pair from being replayed to the same webhook endpoint with the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic` / `X-Shopify-Webhook-Id`) header rewritten to name a different (victim) shop. `HmacValidator.validate` will still return `true` because it only checks the body against the shared secret, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain, together with `body` bytes that were authenticated for a completely different tenant.

The rule the gem should enforce — "the shop that produced/authenticated the payload equals the shop attributed to the payload" — is violated because the `shop` field is acted upon (used for tenant attribution and routing) but is not part of the HMAC-verified data.

### Impact Explanation
This is a cross-tenant confusion vector: an app built on this gem that uses `WebhookMetadata#shop` to select which merchant/session record to update (a common pattern, e.g. "look up Shop X's stored data and apply this order/webhook payload") can be made to apply attacker-supplied, self-authenticated content under a victim shop's identity. Since the HMAC gate is the gem's only advertised integrity/authenticity guarantee for webhooks (`docs` and code both treat `HmacValidator.validate` as sufficient proof of authenticity), and it does not bind the header fields used for tenant attribution, this qualifies as cross-tenant access, matching the Critical impact bucket.

### Likelihood Explanation
Requires only: (1) the attacker has legitimate access to their own shop's app installation (any normal merchant), enabling them to observe one genuine `(raw_body, hmac)` pair delivered to their own server, and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint (which is designed to be internet-reachable). No access to the `client_secret`, no privileged account beyond a self-service store, and no TLS interception is needed — the attacker only needs traffic they themselves legitimately receive.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is HMAC-verified, or otherwise cryptographically tie the header fields to the authenticated body — e.g., include the `shop` domain in `to_signable_string`, or require the host application to independently verify that `request.shop` corresponds to a shop for which this exact raw body/HMAC combination was expected (per-shop secret or nonce). At minimum, document clearly that `shop`/`topic`/`webhook_id` headers are unauthenticated and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` (normal onboarding).
2. Shopify delivers a real webhook to the attacker's endpoint with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Attacker replays the exact same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) succeeds because it only hashes `raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`) against the shared `Context.api_secret_key`.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com", body: <attacker's parsed body> ...)`, so the app processes attacker-controlled content as if it came from the victim's authenticated store.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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
