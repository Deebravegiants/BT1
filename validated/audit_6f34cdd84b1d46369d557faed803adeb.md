Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  while `HmacValidator.validate`/`validate_signature` computes the signature purely over that signable string [2](#0-1) . The `shop` (and `topic`, `webhook_id`, `api_version`) values are read from separate, unsigned HTTP headers [3](#0-2)  and then passed straight into the handler's metadata without any check that they match what was actually signed [4](#0-3) .

### Title
Webhook `shop` (tenant) identity is not bound by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shopify-shop-domain` header — which is *not* covered by that HMAC — to decide which merchant/tenant the event belongs to.

### Finding Description
`HmacValidator.validate` calls `validate_signature`, which computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field [5](#0-4) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , and `hmac` is decoded straight from the `hmac-sha256` header [6](#0-5) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors all read from separate HTTP headers that are never part of the signed payload [3](#0-2) .

`Registry.process` then does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [4](#0-3) 

The identity binding this breaks, stated as an equality that the code assumes but never checks:
`shop-header-bytes-verified-by-HMAC == shop-bytes-delivered-to-handler`

In reality, only `raw_body` is verified by the HMAC; the `shop` byte value handed to the app's webhook handler is whatever is in the (unauthenticated) header, with no cryptographic tie to the signed body.

### Impact Explanation
An app that stores per-webhook data keyed by `data.shop` (the normal, documented pattern shown in the gem's own tests, e.g. `assert_equal(@shop, data.shop)` [7](#0-6) ) trusts this value as the tenant identity. Because `shop` is not bound to the HMAC, a party who possesses one validly-signed webhook body+HMAC pair (e.g. from a webhook legitimately delivered to their own shop, or a body-only replay) can resubmit it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain`/`shopify-shop-domain` header. The signature still validates (it only covers `raw_body`), but the app processes the event as belonging to a different, attacker-chosen shop — a cross-tenant data/event injection.

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint and one previously-observed valid `(raw_body, hmac)` pair for any topic that has a static or attacker-known body shape (or a body they were legitimately sent for their own store), since headers such as `shop-domain` are attacker-controlled and never covered by the signature. No secrets, tokens, or privileged access are required.

### Recommendation
Bind the shop identity to the HMAC-verified content: include the `shop-domain` (and ideally `topic`/`webhook_id`/`api_version`) headers in the signable string used for HMAC verification (matching what Shopify signs) — or otherwise cryptographically authenticate the header set together with the body — before exposing `request.shop` to registered handlers.

### Proof of Concept
1. Attacker's own store legitimately receives a webhook delivery with body `B` and valid header `shopify-hmac-sha256: H` (H = HMAC(secret, B), unknown attacker still gets this pair from Shopify's real delivery).
2. Attacker resends `POST /webhook_endpoint` with the same raw body `B`, same `shopify-hmac-sha256: H`, but header `shopify-shop-domain: victim-shop.myshopify.com` (and matching `shopify-topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` — succeeds, since only `raw_body` is checked [8](#0-7) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` [9](#0-8) , and the app processes/stores data as if the event originated from the victim tenant.

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

**File:** test/webhooks/registry_test.rb (L248-252)
```ruby
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal(@headers["x-shopify-webhook-id"], data.webhook_id)
            assert_equal(@headers["x-shopify-api-version"], data.api_version)
```
