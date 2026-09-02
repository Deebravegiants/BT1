### Title
Webhook HMAC only covers the request body — `shop-domain`/`topic`/`webhook-id` headers are unauthenticated and can be spoofed for cross-tenant confusion ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw HTTP body, then trusts `request.shop`, `request.topic`, and `request.webhook_id` — all of which are read straight from HTTP headers that are **not** included in the signed material. This is structurally identical to the Vultisig bug class: a value that is *acted on* (`shop`, used as the tenant key passed to the handler) is not part of the data that is cryptographically *verified* (only the raw body is HMAC-checked). An attacker who can obtain any one valid `(raw_body, hmac)` pair — trivially available to them by installing the app on their own store and capturing a legitimate webhook delivery for their own shop — can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header. The HMAC check still passes, but the shop identity delivered to the host application's webhook handler is now attacker-chosen rather than the one that was actually verified.

### Finding Description
`Webhooks::Request` builds `hmac` and `to_signable_string` from the raw body only: [1](#0-0) [2](#0-1) 

`shop`, `topic`, and `webhook_id`, however, are pulled from headers that are never part of the signed string: [3](#0-2) 

`Registry.process` validates only the HMAC of the request (i.e., the body), then unconditionally hands `request.shop` (an unauthenticated header value) to the merchant's handler as the tenant identifier: [4](#0-3) 

`HmacValidator.validate` confirms this: it only ever calls `verifiable_query.to_signable_string`, so for webhooks the "verified bytes" and the "acted-upon shop" are two disjoint pieces of the request: [5](#0-4) 

The binding that is broken (expressed as the equality that should hold but does not):
`shop_that_was_HMAC_verified == shop_delivered_to_handler`
In reality, only `raw_body_that_was_HMAC_verified == raw_body`, while `shop_delivered_to_handler` is taken from an unauthenticated header, so the equality above does not hold. Any user who possesses one legitimate `(raw_body, hmac)` pair for topic X of their own shop can present it with a different `shop-domain`/`topic`/`webhook-id` header set and the gem will still report `Utils::HmacValidator.validate(request)` as `true`, dispatching the (still real, but now mis-attributed) payload as if it belonged to another shop or another topic.

### Impact Explanation
This crosses a tenant boundary using no privileged secret: an ordinary merchant who installs the app on their own store can capture a genuine webhook (body + `X-Shopify-Hmac-Sha256`) delivered for their own shop, then POST it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop (or a different `topic`/`webhook-id`). Because the gem's `process` only checks the HMAC of the body, the forged request is accepted as authentic, and the host handler — which relies on `WebhookMetadata#shop`/`#topic` supplied by this gem — will process attacker-controlled (but validly-signed) data under another tenant's identity. This matches the "cross-tenant access" criterion for Critical severity, since the trust boundary between shops is enforced incorrectly by the gem's own webhook verification primitive.

### Likelihood Explanation
Any developer/merchant with a normal app install can trivially capture one legitimate webhook (topics like `app/uninstalled`, `orders/create`, etc. fire routinely) and replay it with modified headers against the same publicly reachable webhook endpoint. No credential, access token, or `client_secret` is required — only the ability to receive one real webhook for their own shop and to freely set headers on their own HTTP request to the app's endpoint. This makes the likelihood high for any app that keys authorization/data-writes off `WebhookMetadata#shop` (which is the documented usage pattern for this gem).

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that host apps must cross-check `request.shop` against a shop for which a session is genuinely on file before acting on the payload, and consider deduplicating/binding by `webhook_id` plus verifying it hasn't been reused with different topic/shop headers.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own store "attacker.myshopify.com"
#    and receives one legitimate webhook, e.g. for "orders/create":
raw_body = '{"id":1,"note":"legit order"}'
valid_hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)
# (attacker learns valid_hmac by simply capturing their own inbound webhook request)

# 2. Attacker replays the same body+hmac to the app's webhook endpoint,
#    but swaps the shop-domain / topic headers:
forged_headers = {
  "shopify-hmac-sha256" => Base64.encode64(Digest.hexdecode(valid_hmac)),
  "shopify-topic" => "customers/data_request", # or any other topic
  "shopify-shop-domain" => "victim-shop.myshopify.com", # not attacker's own shop
  "shopify-webhook-id" => "forged-id",
  "shopify-api-version" => "2024-10",
}
request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. Registry.process only checks the HMAC of raw_body, which still matches:
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true,
#    handler.handle is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "customers/data_request", ...)
#    even though nothing about "victim-shop.myshopify.com" or the topic was ever verified.
```

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
