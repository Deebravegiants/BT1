### Title
Webhook `shop`, `topic`, and `webhook_id` headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) come from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then forwards these unauthenticated header values directly to the webhook handler as the trusted tenant/event identity, allowing a replayed, still-validly-signed body to be relabeled to any shop or topic.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from attacker-controllable HTTP headers, none of which participate in the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then trusts the header-derived `topic` and `shop` to look up a handler and to build `WebhookMetadata`, which is handed to the app's handler as the authenticated tenant/event identity: [3](#0-2) 

This reproduces the exact bug class from the external report: a field that is *acted on* (here, `shop`/`topic`, used as the tenant/event identity binding) is not covered by the integrity check (`hmac`) that is supposed to bind it. Since a single app's `client_secret` is shared across every installed shop, any merchant who legitimately installs the app can capture a validly HMAC-signed webhook body delivered to their own shop, then replay that exact `raw_body` + `hmac` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for a different, victim shop. `HmacValidator.validate` will still pass because it only ever checks `body` against `hmac`: [4](#0-3) 

The handler then receives `WebhookMetadata` claiming the forged `shop`/`topic`, even though the signature never bound those values.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate merchant with respect to their own shop (i.e., an "unprivileged" party from the perspective of any other tenant) can cause the app to process an event as if it belongs to a different shop, because the `shop` identity is never bound by the HMAC. Depending on how the host app's webhook handler uses `WebhookMetadata.shop` (e.g., to look up a session/access token or to write tenant-scoped data), this enables cross-tenant confusion of webhook data/state — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to have received at least one legitimate, HMAC-signed webhook to their own shop (readily obtainable by installing the app themselves) and to be able to POST arbitrary headers to the app's public webhook endpoint (a public, unauthenticated HTTP endpoint by design). No access token, `client_secret`, or privileged credential is required.

### Recommendation
Include the identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signed content verified by `HmacValidator`, or otherwise cryptographically bind them (e.g., derive them only from a value that is itself covered by the signature, or require the webhook consumer to cross-check `shop` against a value obtained through an authenticated channel) instead of trusting raw headers once only the body's HMAC has been checked.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; Shopify delivers a real webhook with body `B` and header `x-shopify-hmac-sha256: H` (valid signature of `B` under the shared `client_secret`), plus `x-shopify-shop-domain: attacker.myshopify.com` and `x-shopify-topic: orders/create`.
2. Attacker replays the same body `B` and signature `H` to the app's public webhook endpoint, but with headers rewritten to `x-shopify-shop-domain: victim.myshopify.com` (and optionally a different registered `x-shopify-topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ...)`, even though `victim.myshopify.com` was never covered by the HMAC.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
