This confirms the exact identity-binding gap: `Registry.process` validates only `Utils::HmacValidator.validate(request)`, whose signable string is `request.to_signable_string` = `@raw_body` [1](#0-0) . Meanwhile `request.shop`, `request.topic`, and `request.webhook_id` are read straight from HTTP headers that are never mixed into the signable string or otherwise checked against the HMAC [2](#0-1) . `Registry.process` then dispatches to the app's handler using that unauthenticated `request.shop` as the tenant identifier [3](#0-2) .

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)` [3](#0-2) . The HMAC's signable string is defined as `@raw_body` only [1](#0-0) , while the `shop` (and `topic`, `webhook_id`) values used to route and attribute the event are pulled unauthenticated straight from HTTP headers [2](#0-1) . Because the app's `client_secret`/`api_secret_key` used to compute the HMAC is shared across every merchant that installs the app (it is not shop-specific — see `HmacValidator.validate_signature` signing with `Context.api_secret_key`) [4](#0-3) , any merchant that has installed the app can capture a legitimately-signed `(raw_body, hmac)` pair delivered to their own webhook endpoint and replay it against the app's endpoint with the `shopify-shop-domain` header swapped to a victim shop's domain. The HMAC validation still succeeds because it never covers the shop header, and the handler is invoked believing the event originated from the victim shop.

### Finding Description
The identity binding that should hold is: `shop value trusted by the handler == shop value cryptographically bound by the HMAC`. In this code, that equality is broken:
- Before request: a merchant M installs the app and receives a genuine webhook `(raw_body_M, hmac = HMAC(api_secret_key, raw_body_M), shop-domain: M)`.
- Attack: M resends the same `raw_body_M`/`hmac` pair to the app's webhook endpoint, but with header `shopify-shop-domain` set to victim shop `V`.
- `HmacValidator.validate` recomputes `HMAC(api_secret_key, raw_body_M)` and compares to the supplied `hmac` — it matches, because the signable string never included the shop header [1](#0-0) [5](#0-4) .
- `Registry.process` then builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` and calls `handler.handle` with `shop` equal to the attacker-chosen `V` [6](#0-5) .

The app's handler, trusting `data.shop` as the authenticated tenant (this is the documented contract, as seen in the test asserting `data.shop` equals the header value) [7](#0-6) , will act on victim `V`'s tenant using data that Shopify never actually sent for `V`.

### Impact Explanation
This breaks the shop-authenticated-vs-shop-trusted binding across tenants: any merchant who has legitimately installed the app (an "unprivileged" party relative to other tenants of the same app) can forge webhook deliveries that the app attributes to a different merchant's shop, since `api_secret_key` is shared by all installs and the shop identity is not part of the signed payload. Depending on how the app's `WebhookHandler#handle` implementation uses `data.shop` (e.g., to trigger data deletion/redaction for mandatory topics like `shop/redact` or `customers/redact`, or to update per-shop state), this can result in cross-tenant data corruption or disclosure.

### Likelihood Explanation
Exploitation requires only that the attacker has installed the app on their own store (a normal, unprivileged action) and can capture one legitimate webhook delivery to replay with a modified header — no access token, `client_secret`, or elevated privilege is required, and no interaction with the victim is needed.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed payload verification — e.g., include the `shopify-shop-domain` header value in the string that is HMAC-verified, or independently verify that the shop domain in the body/headers matches an expected value tied to the webhook subscription, rather than trusting an unauthenticated header for tenant attribution.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com`; capture a webhook Shopify sends to the app, e.g. body `{}` with headers `x-shopify-hmac-sha256: <valid-hmac>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: shop/redact`.
2. Resend the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [1](#0-0) .
4. The app's registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing it to act as though Shopify sent this event for `victim.myshopify.com` [6](#0-5) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** test/webhooks/registry_test.rb (L271-276)
```ruby
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal("b1234-eefd-4c9e-9520-049845a02082", data.webhook_id)
            assert_equal("2024-01", data.api_version)
            handler_called = true
```
