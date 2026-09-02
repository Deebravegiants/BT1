### Title
Webhook HMAC only covers the request body, letting an attacker forge the `shop-domain`, `topic`, and `webhook-id` headers to spoof cross-tenant webhook delivery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The report describes a "skim-aware" gap: a downstream computation trusts a value (`couponUsdcAmount`) without accounting for another value (`distributionSkimBps`) that silently changes what's actually delivered, breaking the equality between "amount promised" and "amount paid." The analogous class in this gem is a verification/attribution mismatch: `ShopifyAPI::Webhooks::Registry.process` verifies an HMAC that covers only the raw body, then trusts unsigned header-derived fields (`shop`, `topic`, `webhook_id`, `api_version`) for tenant attribution and dispatch. The equality that should hold — "HMAC-verified bytes == bytes used to identify the shop/topic" — does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes and compares the HMAC solely against that `to_signable_string` value: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are never part of the signed payload: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately dispatches using these unsigned fields, including `request.shop`, to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because only the body bytes are authenticated, any request whose body produces a matching HMAC (e.g. a genuine webhook captured from the attacker's own shop, where the body content is attacker-influenced/known, such as a product-update or order-update payload) can be replayed to the same endpoint with the `shop-domain` header rewritten to a victim shop's domain, and/or with a different `topic`/`webhook-id`. The signature check still passes because those header values were never covered by the HMAC, but the handler receives them as if they were authentic, trusted per-tenant identifiers.

This is the same structural defect as the report's "skim-aware" bug: a field that materially affects the outcome (here, tenant attribution) is excluded from the verification that's supposed to bind the whole message together.

### Impact Explanation
This breaks the equality `HMAC-covered bytes == bytes used for shop/topic attribution`. An attacker who can obtain any one legitimately-signed webhook body/HMAC pair (e.g., from their own installed instance of the app) can forge the shop identity on replay, causing the app to process/react to a webhook as if it came from a different, victim merchant's shop. Depending on how the host app uses `WebhookMetadata#shop`/`#topic` (e.g., looking up sessions, updating tenant-scoped data, or triggering shop-specific side effects), this is a cross-tenant identity spoofing primitive — satisfying the "cross-tenant access" Critical/High impact bucket, since the shop-authenticated-by-signature does not equal the shop-attributed-and-acted-on.

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the app on some shop (an unprivileged action any merchant/developer can do to obtain one valid signed webhook), and (2) network access to POST to the app's webhook endpoint with modified headers. No access to `api_secret_key`, access tokens, or the app owner's credentials is required — only a single previously-observed valid `(raw_body, hmac)` pair, which is obtainable by any user who can install the app on a store they control and observe its own outgoing webhooks.

### Recommendation
Bind the identifying headers into the HMAC-signed payload, or otherwise ensure that any field used for tenant/topic dispatch (`shop`, `topic`, `webhook_id`, `api_version`) is derived only from a source that Shopify itself authenticates end-to-end (mTLS/IP allow-listing is not something this gem can rely on). At minimum, document that `Registry.process` must be paired with an out-of-band, non-header-derived shop verification (e.g., confirming the target shop matches a shop that is expected to be receiving this specific webhook based on route/tenant binding, not header content) before dispatch.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook event with an attacker-influenced body (e.g., update a product's title to a fixed value), capturing the resulting `raw_body` and `x-shopify-hmac-sha256` header sent by Shopify to the app's webhook endpoint.
2. Replay that exact `raw_body` and `hmac` to the same endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the HMAC — validation succeeds.
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built using the attacker-supplied `shop-domain` header and passed to the registered handler, which processes the event as if it originated from `victim.myshopify.com`.

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
