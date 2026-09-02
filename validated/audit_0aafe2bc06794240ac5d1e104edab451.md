## Analysis

The report's bug class — *"a value is trusted and acted upon, but the integrity check that is supposed to gate it doesn't actually cover that value"* — maps directly onto `ShopifyAPI::Webhooks::Request` / `ShopifyAPI::Webhooks::Registry`.

`Registry.process` gates all webhook handling on a single check: `Utils::HmacValidator.validate(request)`, and only that. [1](#0-0) 

That validator computes the HMAC exclusively over `request.to_signable_string`, which returns the raw request body — nothing else: [2](#0-1) [3](#0-2) 

But `shop`, `topic`, and `webhook_id` are read from separate, unsigned headers, and are exactly the fields the handler uses to identify which tenant the event belongs to: [4](#0-3) [5](#0-4) 

The binding that is supposed to hold is: `hmac_valid(body) == shop_identity_trusted`. In reality `hmac_valid(body)` only proves the body bytes are untampered under the app's secret; it says nothing about which shop the request is for. Any request whose body byte-for-byte matches a body that was ever legitimately signed for the app (e.g., a webhook the attacker's own shop received, or any topic whose body content the attacker can predict/replay) will pass `HmacValidator.validate` regardless of what `shopify-shop-domain` / `shopify-topic` / `shopify-webhook-id` headers are sent alongside it. An unprivileged internet user who operates their own shop installed on the app receives genuine, validly-HMAC'd webhook deliveries from Shopify for their own tenant; they can resend that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop. The library will treat it as an authentic event for the victim shop, dispatching `WebhookMetadata.new(shop: <victim>, ...)` to the app's handler.

This is a direct cross-tenant identity-confusion vulnerability introduced by the library's own validation logic omitting the identifying headers from the signed payload, reachable by any unprivileged actor who can send HTTP requests to the app's public webhook URL — no access token, no `client_secret`, no privileged account needed.

### Title
Webhook shop/topic/webhook-id identity headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (`File: lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely via `Utils::HmacValidator.validate(request)`, which signs only the raw request body (`Request#to_signable_string`). The `shop-domain`, `topic`, and `webhook-id` headers used to route and attribute the webhook to a tenant are not included in the signed data at all.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only [6](#0-5) , and `HmacValidator.validate_signature` computes/compares the HMAC purely against that string [7](#0-6) . Meanwhile `Registry.process` trusts `request.shop`, `request.topic`, and `request.webhook_id` — all sourced from separate, unauthenticated headers [4](#0-3)  — to build the `WebhookMetadata` dispatched to the app's registered handler [1](#0-0) . The equality the code implicitly assumes — "HMAC-valid body ⇒ headers describing that body's origin (shop/topic/id) are trustworthy" — does not hold, because those headers are never part of the signed bytes.

### Impact Explanation
Any raw body that was ever legitimately HMAC-signed by the app's secret (including ones an attacker legitimately received for their own installed shop) can be resent with an arbitrary `shopify-shop-domain` header. `Registry.process` will accept the HMAC as valid and hand the handler data claiming to be from a different (victim) shop, causing cross-tenant data confusion inside the merchant's app (e.g., an order/customer webhook processed under the wrong shop's tenant context, corrupting or leaking per-tenant state). This satisfies the "cross-tenant access" Critical impact category.

### Likelihood Explanation
High. Exploitation requires no secrets — only the ability to install the app on any shop (or otherwise obtain one validly-signed webhook body/HMAC pair) and the ability to POST to the app's public webhook endpoint with modified headers, both of which are available to an ordinary unprivileged internet user / merchant.

### Recommendation
Bind the identifying headers into the HMAC-verified data, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the verified payload before using them for tenant routing — e.g., include them in `to_signable_string`, or independently validate `shop` against the session/tenant the webhook subscription was registered for, rather than trusting the header verbatim once body-HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook event (e.g., `orders/create`) with a body they can predict/control (order fields they set).
2. Shopify delivers the webhook with headers `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: <valid HMAC of raw_body>`.
3. Attacker resends the identical `raw_body` and `shopify-hmac-sha256` value to the app's webhook endpoint, but replaces `shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks the (unchanged) body against the (unchanged) HMAC [8](#0-7) ; `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the handler [5](#0-4) , causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

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
