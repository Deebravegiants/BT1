Confirmed: `Registry.process` uses `Utils::HmacValidator.validate(request)` to authenticate, then trusts `request.topic`, `request.shop`, and `request.webhook_id` — all sourced purely from unauthenticated HTTP headers — to build `WebhookMetadata` passed to the app's handler [1](#0-0) .

### Title
`to_signable_string` signs body only, allowing header spoofing (topic/shop/webhook-id) with a validly-signed body — cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `HmacValidator.validate` never covers the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers [2](#0-1) . An attacker who owns a shop and receives a legitimately-signed webhook body from Shopify can resend that exact body to the app's webhook endpoint with arbitrary `shop-domain`/`topic`/`webhook-id` headers, and `HmacValidator.validate` will still accept it because it only recomputes the HMAC over the body [3](#0-2) .

### Finding Description
The broken binding: the equality `bytes(compute_signature input) == bytes(parsed for topic/shop/webhook_id)` is assumed to hold but does not. `compute_signature` is invoked with `verifiable_query.to_signable_string`, which is `@raw_body` only [4](#0-3) [2](#0-1) . Meanwhile `Registry.process` reads `request.topic`, `request.shop`, `request.webhook_id` — all parsed straight from HTTP headers via `shopify_header`, never covered by the signature — and forwards them unauthenticated into `WebhookMetadata`, which the host app's `WebhookHandler#handle` trusts as the tenant/topic identity [5](#0-4) [6](#0-5) .

Exploit flow: attacker installs the app on their own shop, triggers/receives a topic they control (e.g. `orders/create`) with a body containing attacker-influenced fields (order note, line item titles, customer email, etc.), capturing the valid `raw_body` + `X-Shopify-Hmac-Sha256` pair signed with the app's shared `api_secret_key` (same secret is used for every shop installed on that app, since `Context.api_secret_key` is a single value, not per-shop [7](#0-6) ). The attacker then POSTs that identical `raw_body` directly to the app's webhook endpoint but swaps `X-Shopify-Shop-Domain` to the victim's domain and/or the `X-Shopify-Webhook-Id`/topic headers. `HmacValidator.validate` recomputes HMAC only over `raw_body`, matches, and returns `true`; `Registry.process` then dispatches to the handler claiming the payload originated from the victim shop.

Existing guards do not catch this: `HmacValidator.validate` only checks the HMAC against `to_signable_string` (body) [3](#0-2) ; there is no `ShopValidator.sanitize!`, no per-shop secret, and no header-inclusion in the signed payload anywhere in `Request` or `HmacValidator`.

### Impact Explanation
Any app relying on `request.shop`/`request.topic`/`request.webhook_id` from `WebhookMetadata` to key data access (e.g., "look up shop record for `data.shop`, apply `data.body` to it") can be made to write/process attacker-supplied body content under a victim shop's identity, since the shop header is not authenticated. This is cross-tenant: one shop's signed payload can be replayed as if attributed to another merchant, matching "Critical - cross-tenant access" per the rules. Repeatable for every webhook the attacker's own shop can trigger, against any known/guessable victim shop domain.

### Likelihood Explanation
Preconditions: attacker needs only their own free/dev shop with the app installed (standard, unprivileged) and knowledge of (or ability to guess) a target shop's `.myshopify.com` domain, which is often public. No secrets are needed. Cost is a single legitimate webhook trigger plus a replayed HTTP POST with modified headers — trivially repeatable.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string, or otherwise bind them cryptographically to the payload before validation, so `HmacValidator.validate` authenticates the full identity tuple, not just the body bytes.

### Proof of Concept
Minitest (WebMock/Mocha, no live shop):
```ruby
# stub Context.api_secret_key to a known value
raw_body = '{"id":1,"note":"attacker-controlled"}'
headers_a = { "x-shopify-topic" => "orders/create", "x-shopify-hmac-sha256" => valid_hmac,
              "x-shopify-shop-domain" => "attacker.myshopify.com", "x-shopify-webhook-id" => "1" }
headers_b = headers_a.merge("x-shopify-shop-domain" => "victim.myshopify.com",
              "x-shopify-webhook-id" => "999")

req_a = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers_a)
req_b = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers_b)

assert_equal req_a.hmac, req_b.hmac
assert ShopifyAPI::Utils::HmacValidator.validate(req_a)
assert ShopifyAPI::Utils::HmacValidator.validate(req_b)  # accepted despite different shop/webhook-id
assert_equal "victim.myshopify.com", req_b.shop           # unauthenticated header now trusted downstream
```
This demonstrates both headers pass validation identically despite differing shop/webhook-id, confirming the byte-identity invariant is violated at the header level while the body-only HMAC still validates.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
