### Title
Webhook HMAC does not bind the `shop-domain` header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , so the HMAC verified by `Utils::HmacValidator.validate` in `Registry.process` only authenticates the request body bytes — never the `shop-domain`, `topic`, `webhook-id` or `api-version` headers. `Registry.process` nonetheless trusts `request.shop` (read straight from the unauthenticated header) when constructing the `WebhookMetadata` handed to the app's handler [2](#0-1) . Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app (it is not per-shop), any merchant who has installed the app can capture a legitimately-signed webhook body from their own shop and replay it with a different `shop-domain` header to make the gem hand the app a webhook that is falsely attributed to another tenant.

### Finding Description
The identity binding that should hold is:
`shop_authorized_by_HMAC == shop_used_to_attribute_the_webhook_payload`

In this gem the left side is empty — `to_signable_string` signs only `@raw_body`:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

while the right side is taken from an attacker-controllable header with no cross-check against anything covered by the HMAC:
```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` to the handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [2](#0-1) 

Because the same `api_secret_key` is used by Shopify to sign webhooks for *every* shop that has the app installed, any merchant of the app is a valid holder of legitimately-signed `(body, hmac)` pairs for their own shop. Nothing in `HmacValidator.validate` or `Registry.process` ties that signature to the specific `shop-domain` header, so the pair can be replayed against the app's webhook endpoint with an arbitrary `shop-domain` (and `topic`/`webhook-id`) header and will still pass validation.

### Impact Explanation
This breaks the tenant isolation the gem is supposed to provide to the hosting app: `Registry.process` will hand the app data (`WebhookMetadata#shop`) that purports to come from a shop the request never actually originated from. Any app that uses `data.shop` from the processed webhook to decide which merchant's records to create/update/delete (a normal and expected usage pattern, shown in the gem's own test helpers [4](#0-3) ) can be made to attribute attacker-supplied content to a victim shop — a cross-tenant data-integrity violation reachable by any unprivileged merchant who has installed the app on their own store, with no access token, `api_secret_key`, or other privileged material required.

### Likelihood Explanation
Any Shopify merchant can install a public app, trigger a webhook for their own store (e.g. `orders/create` with attacker-chosen order data), and capture the resulting `(raw_body, X-Shopify-Hmac-Sha256)` pair from their own delivered webhook. Replaying that exact body/HMAC to the app's webhook endpoint with a different `X-Shopify-Shop-Domain` header requires nothing beyond a basic HTTP client, making this trivially and repeatably exploitable by any internet user willing to install the app.

### Recommendation
Include the shop (and ideally topic/webhook-id/api-version) in the value that is HMAC-verified, or otherwise cryptographically bind the header fields the gem trusts to the signed payload before using them. At minimum, `Registry.process` should reject requests whose `shop` cannot be corroborated by data that is actually covered by the HMAC (e.g. validate against a shop known from an authenticated session/registration rather than trusting the raw header), consistent with the Check-Effects/verify-what-you-use principle referenced in the bug-class hint.

### Proof of Concept
1. App developer installs their app; secret `api_secret_key` is fixed across all shop installs.
2. Attacker installs the same public app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g., creates an order with attacker-chosen JSON fields), receiving from Shopify a POST with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and the raw JSON body.
3. Attacker resends the identical raw body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over `to_signable_string` (== `@raw_body` only) and it matches, so validation succeeds.
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)` and invokes the app's handler, which now processes attacker-controlled content as if it belonged to `victim-shop.myshopify.com`.

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

**File:** test/webhooks/registry_test.rb (L241-253)
```ruby
      def test_process_with_response_as_struct
        modify_context(response_as_struct: true)

        handler_called = false

        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal(@headers["x-shopify-webhook-id"], data.webhook_id)
            assert_equal(@headers["x-shopify-api-version"], data.api_version)
            handler_called = true
```
