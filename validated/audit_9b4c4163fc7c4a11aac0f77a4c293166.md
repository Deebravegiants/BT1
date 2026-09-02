### Title
Webhook `shop-domain` header is trusted for shop identity but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop identity used by the webhook handler is taken from an unsigned HTTP header. An attacker who can obtain one validly-signed `(body, hmac)` pair (e.g., by triggering any webhook event on their own store) can replay that exact body to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop, and the signature check will still pass.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, a value that plays no part in the HMAC computation: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes and compares the signature over `to_signable_string` (i.e., the body): [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then immediately forwards `request.shop` (an unauthenticated header value) to the handler as the trusted tenant identity for the event: [4](#0-3) 

The binding that should hold is: `bytes verified by HMAC == bytes the application treats as authenticated (shop, topic, webhook_id, api_version)`. Here `bytes verified` = `raw_body` only, while `bytes trusted for shop identity` = the `shop-domain` header. Because the header is outside the signed payload, the two are decoupled: any request with a previously-observed valid `(body, hmac)` pair can be replayed with an arbitrary `shop-domain` header and will still pass `HmacValidator.validate`.

An attacker who is a legitimate merchant of the installing app (or otherwise can capture one genuine signed webhook delivery from Shopify to the app, which is not privileged/secret-holding access) can:
1. Trigger a webhook event on their own shop (e.g. `orders/create`) and capture the raw body + `X-Shopify-Hmac-Sha256` header Shopify sends to the app's public webhook endpoint.
2. Replay that same `(body, hmac)` pair to the app's webhook endpoint, but with `X-Shopify-Shop-Domain` changed to a victim shop that also installed the app.
3. `Utils::HmacValidator.validate` succeeds because the signature only covers the body, which is unchanged. `Registry.process` then calls the handler with `WebhookMetadata.new(... shop: request.shop ...)` pointing at the victim shop.

If the host application's webhook handler uses `data.shop` to look up sessions/access tokens or to determine which tenant's data to mutate (a very common pattern, e.g. via `ShopifyApp`'s webhook job base classes), this results in the attacker's forged webhook data being processed/attributed under a victim shop's identity — a cross-tenant identity-binding break analogous to the TWAP report's root cause (only a fraction of the relevant state is actually protected/verified while the rest is blindly trusted).

### Impact Explanation
This crosses a tenant boundary: content is authenticated as coming from Shopify (valid HMAC over the body), but the shop the content is *attributed to* is not authenticated at all. Any app logic that keys off `WebhookMetadata#shop` (session lookup, per-shop data writes, deletion triggers such as `shop/redact` or `customers/data_request`, etc.) can be made to act on the wrong tenant. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is medium: it requires the attacker to have at least one shop that installed the target app (to generate a genuinely-signed webhook body) and knowledge of the app's public webhook endpoint (readily discoverable), but does not require the `api_secret_key`, an access token, or any other stolen credential. No sophisticated setup beyond replaying an HTTP request with a modified header is needed.

### Recommendation
Bind the shop (and other trusted metadata such as topic/webhook-id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed payload before it is passed to `handler.handle`. Concretely:
- Include the shop domain (and other identity-bearing headers) in `to_signable_string` so `HmacValidator.validate` fails if any of them are altered, or
- Independently verify that `request.shop` matches an expected/authorized session for the currently active webhook subscription before invoking the handler, rather than trusting the header at face value.

### Proof of Concept
```ruby
# Attacker owns shop "attacker.myshopify.com" which has the app installed.
# Step 1: trigger any webhook (e.g. orders/create) on attacker's shop and capture:
raw_body = '{"id":123,"note":"hello"}'
valid_hmac_from_shopify = "<base64 hmac Shopify computed over raw_body with the app's secret>"

# Step 2: replay to the app's public webhook endpoint with a forged shop header
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_from_shopify, # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, NOT covered by hmac
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
``` [4](#0-3) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
