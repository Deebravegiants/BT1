## Finding

The webhook signature verification in this gem only covers the request body — never the `shop`, `topic`, `webhook-id`, or `api-version` headers that the library treats as trusted identity fields when dispatching to app handlers.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the HMAC at all: [2](#0-1) 

`Registry.process` validates only the HMAC (which is computed exclusively over the body) and then dispatches to the app handler using the unverified header-derived fields: [3](#0-2) 

`HmacValidator.validate` signs/verifies `verifiable_query.to_signable_string`, which for `Request` is body-only: [4](#0-3) 

### Equality that should hold but doesn't

`shop` (bytes covered by the HMAC that Shopify computed) should equal `shop` (bytes the app trusts for tenant attribution). Here, the HMAC only proves "this body byte-string came from Shopify with this app's secret" — it says nothing about which shop, topic, or webhook that body belongs to.

### Exploitability

Shopify sends a valid `raw_body` + `hmac-sha256` pair to every shop that installs the app, including a shop an attacker fully controls (any developer can spin up a free dev/partner store and install their own target app, or any real merchant can install the app themselves). Once they possess one legitimately-signed `(raw_body, hmac)` pair from their own shop's webhook delivery, they can replay that exact body/hmac pair to the app's public webhook endpoint while freely substituting the `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers to any value — the HMAC check in `HmacValidator.validate` still passes because none of those headers are part of `to_signable_string`. The app's handler receives a `WebhookMetadata` claiming to be from a different, victim shop and topic, and will process/store that (attacker-supplied) body content as if it belongs to the victim tenant.

This breaks the same class of identity binding the external report describes (an access-controlled operation performed using an unverified identity claim) — here manifesting as: **shop/topic/webhook_id claimed by headers ≠ shop/topic/webhook_id actually covered by the Shopify HMAC**.

### Title
Webhook shop/topic/webhook-id headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body. The `shop`, `topic`, `webhook_id`, and `api_version` fields that `Registry.process` passes on to the app's webhook handler as trusted tenant/context identifiers are read from HTTP headers that are entirely outside the HMAC's scope.

### Finding Description
Any party who can obtain one legitimately Shopify-signed `(raw_body, hmac)` pair — trivially achievable by installing the target app on a shop they control — can replay that pair to the app's public webhook endpoint with arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` header values. `Utils::HmacValidator.validate` only re-derives the HMAC over `@raw_body` [5](#0-4) , so the forged headers pass verification unchanged, and `Registry.process` forwards them straight into `WebhookMetadata` for the registered handler [6](#0-5) .

### Impact Explanation
This is a cross-tenant integrity break: the app's webhook handler will act on data it believes originates from shop B's `orders/create` (or any other topic), when in fact the signed content and shop context were supplied by attacker-controlled shop A. Depending on what the host app does in its handler (e.g., write to shop-B-keyed storage, trigger shop-B side effects), this enables cross-tenant data corruption/injection using only the ability to install the app on any shop — meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Any developer/partner can install a target app on a store they control and receive genuinely-signed webhook deliveries at will, then replay the body+hmac to the app's public endpoint with forged headers. No privileged credentials, `api_secret_key`, or access token are required — only the ability to install the app on an attacker-owned shop, which is the normal, unprivileged installation flow.

### Recommendation
Bind the header-derived identity fields into the signed payload before verification — e.g., include `shop`, `topic`, and `webhook_id` in the string that is HMAC-verified (as Shopify's own signature scheme intends), or independently verify that the `shop-domain` header matches a shop with an active, expected subscription/session before trusting it. At minimum, `to_signable_string` should not treat headers used for tenant/topic dispatch as out-of-band from the cryptographic check.

### Proof of Concept
1. Install the target app (using this gem) on an attacker-controlled dev store `attacker.myshopify.com`, triggering a real webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid, computed by Shopify with the app's real secret).
2. Capture `(B, H)` from the attacker's own endpoint logs.
3. POST to the app's public webhook endpoint with `raw_body = B`, headers `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: victim.myshopify.com`, `x-shopify-topic: orders/create` (or any other registered topic), and any desired `x-shopify-webhook-id`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [7](#0-6) .
5. The registered handler is invoked with `WebhookMetadata` claiming `shop: "victim.myshopify.com"` [8](#0-7) , causing the app to process attacker-controlled content under the victim shop's identity.

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
