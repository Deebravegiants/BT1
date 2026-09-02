### Title
Webhook `shop-domain` Header Is Not Covered by HMAC, Allowing Cross-Tenant Shop Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and passed straight through to the application's webhook handler. Any unprivileged internet user who can obtain one legitimately-signed webhook body (e.g. by installing the app on their own store and triggering a webhook) can replay that body to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header, and the HMAC check will still pass because the header is not part of the signed content.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled unauthenticated from headers: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over the raw body only via `VerifiableQuery`/`HmacValidator`), then immediately builds `WebhookMetadata` using `request.shop`, which was never covered by that HMAC: [3](#0-2) 

`HmacValidator.validate` computes the signature from `verifiable_query.to_signable_string` (the raw body for webhooks) and compares it against the `hmac` header: [4](#0-3) 

The broken identity binding is:
`shop == HMAC-authenticated shop` is expected, but in practice `shop == unauthenticated header value`, since only the body bytes are covered by the HMAC.

### Impact Explanation
Since the webhook endpoint is a public HTTP endpoint (that's the nature of webhook delivery — Shopify posts to a URL the app exposes), any internet user can send a raw POST to it directly, not just Shopify's infrastructure. An attacker who has legitimately installed the app on their own shop (an unprivileged, self-service action) can capture a validly-signed webhook body+HMAC pair from their own shop, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value naming a victim shop. The signature check in `HmacValidator.validate` still succeeds because it only verifies the raw body bytes, not the shop header. The application's webhook handler then processes attacker-controlled body content as if it originated from the victim shop's `WebhookMetadata#shop`, which can lead to cross-tenant data corruption (e.g., an app that keys internal state, orders, or customer records by `data.shop` from `WebhookMetadata`) — a cross-tenant integrity/access violation.

### Likelihood Explanation
Any user can self-install the app on a store they control (no special privileges, no leaked secrets, no access token needed) to obtain a valid signed webhook body, and the endpoint is reachable by design over the public internet. This is a straightforward, repeatable attack requiring only normal app installation and basic HTTP tooling.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) identifiers into the HMAC-covered content, or otherwise cryptographically bind the header values to the verified body (e.g., require the consuming application to independently confirm that the shop asserted in the header actually owns the resources referenced inside the verified body, or refuse processing unless the shop header matches a shop the app has an active, verified session/install for). At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted as an identity boundary by consuming applications without additional server-side shop verification.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` (self-service, unprivileged).
2. Attacker triggers a webhook (e.g., `orders/create`) on their own store, capturing the raw body and the valid `x-shopify-hmac-sha256` value Shopify sent.
3. Attacker POSTs to the app's public webhook endpoint with the same raw body and HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds since it only hashes `@raw_body`.
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` and passed to the app's registered handler, which processes attacker-controlled data under the victim's identity.

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
