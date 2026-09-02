## Title
Webhook `shop` (tenant) identifier is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts the tenant identifier (`shop`) from an HTTP header that is never included in the HMAC-signed payload. `ShopifyAPI::Utils::HmacValidator` only verifies the raw request body, so any request whose body+HMAC pair is valid for the app's shared `api_secret_key` will pass verification regardless of which `shop-domain` header value accompanies it. Because the webhook HMAC secret (`api_secret_key`) is shared across *every* shop that installs the app (it is not shop-specific), a party who has legitimately installed the app on their own shop can capture one of their own valid `(raw_body, hmac)` webhook deliveries and replay it to the app's public webhook endpoint with an arbitrary `shop-domain` header, causing the library to report that event as coming from a different (victim) shop.

### Finding Description
The bound identity broken here is: `shop reported to the handler == shop the HMAC actually authenticates for`. In practice, the code implements:

`request.shop` (used as tenant key) != `request.to_signable_string` (what is actually HMAC-verified)

- `ShopifyAPI::Webhooks::Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

- `#to_signable_string`, the value that actually gets HMAC-verified, is only the raw body — it does **not** include the shop domain, topic, webhook id, or api version headers: [2](#0-1) 

- `HmacValidator.validate` computes/compares the signature exclusively over `to_signable_string`, using the app-wide `Context.api_secret_key` (the same secret for all installed shops): [3](#0-2) 

- `Registry.process` only calls `Utils::HmacValidator.validate(request)` and then trusts `request.shop` to build the `WebhookMetadata` handed to the application's handler: [4](#0-3) 

Since `Context.api_secret_key` is one value for the whole app (shared across all merchant shops), and the HMAC never binds the body to a specific shop, any body+HMAC pair that is valid for shop A is *also* valid when relabeled with shop B's domain — the validator has no way to detect the substitution.

### Impact Explanation
This breaks tenant isolation (cross-tenant access), which the rules classify as **Critical**. An attacker who is themselves a legitimate (but malicious) merchant on the platform can:
1. Install the app on their own shop and receive real webhook deliveries (valid `raw_body` + `hmac`).
2. Replay that exact `raw_body`/`hmac` pair directly to the app's public webhook endpoint, but with the `shopify-shop-domain` header changed to a victim shop's domain.
3. `Registry.process` will pass HMAC validation (it never looks at the shop header) and hand the handler a `WebhookMetadata` claiming the event is from the victim shop, as demonstrated by the test asserting `data.shop == @shop` purely from the header value: [5](#0-4) 

Any host application that uses `data.shop` from this gem to look up per-tenant state (e.g., to update a specific merchant's records, billing, or entitlements) can be tricked into acting on the wrong tenant's behalf.

### Likelihood Explanation
Any app developer who installs their own (or any) instance of the app can generate a valid body/HMAC pair essentially at will (by triggering any webhook topic on their own shop), then relay it with a forged `shop-domain` header to the same public endpoint. No access to `api_secret_key`, access tokens, or the victim's credentials is required — only network access to the app's publicly reachable webhook route. This is a low-effort, repeatable attack once the attacker controls one installed instance of the app.

### Recommendation
Bind the shop identity into what is actually verified. Include the shop domain (and ideally topic/webhook id) in the value that `HmacValidator` verifies, or require that `Request` validation cross-checks that the raw body's embedded shop identity (if resolvable, e.g. by decoding the JSON payload's shop id) matches the `shop-domain` header before trusting it. At minimum, document/enforce that `request.shop`/`WebhookMetadata#shop` must never be trusted for tenant selection without an independent, cryptographically-bound confirmation of tenant identity (e.g., correlating against a per-shop session/access token already on file, rather than the raw header).

### Proof of Concept
```ruby
# Attacker has legitimately installed the app on their own shop "attacker.myshopify.com"
# and received one real webhook delivery from Shopify:
raw_body = '{"id":1,"note":"hello"}'
real_hmac_b64 = "..."  # captured from a genuine Shopify webhook delivery to attacker's own shop

# Attacker now POSTs directly to the app's public webhook endpoint,
# reusing the same body+hmac but spoofing the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => real_hmac_b64,     # still valid, body unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation succeeds (only raw_body is checked),
#    handler receives WebhookMetadata with shop: "victim-shop.myshopify.com"
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** test/webhooks/registry_test.rb (L246-252)
```ruby
        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal(@headers["x-shopify-webhook-id"], data.webhook_id)
            assert_equal(@headers["x-shopify-api-version"], data.api_version)
```
