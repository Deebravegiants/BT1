This confirms the vulnerability: `ShopifyAPI::Webhooks::Registry.process` at [1](#0-0)  validates only the HMAC of the raw body via `Utils::HmacValidator.validate(request)`, and then constructs `WebhookMetadata` (including the `shop` field) directly from unverified HTTP headers, and dispatches it to the app's `WebhookHandler#handle`.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from attacker-reachable HTTP headers [3](#0-2) . `Registry.process` accepts the request as valid as long as `Utils::HmacValidator.validate(request)` succeeds against the body [1](#0-0) , and then blindly trusts `request.shop` when building the `WebhookMetadata` passed to the host app's handler [4](#0-3) .

### Finding Description
The identity binding that should hold is: **the `shop` value delivered to the app's webhook handler == the shop for which Shopify computed the HMAC over the delivered body**. In this gem, only the request body is fed into `to_signable_string`; the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are excluded from the signed payload [2](#0-1) . Since Shopify apps share one `api_secret_key` for HMAC across all shops that install the app (this is not a per-shop secret) [5](#0-4) , a valid `(raw_body, hmac)` pair captured from one shop's webhook delivery remains cryptographically valid for that same app regardless of which shop's header values accompany it.

An unprivileged actor who can observe one legitimate webhook delivery for their own shop (a normal merchant with the app installed can do this trivially, e.g. via a topic like `orders/create` that echoes attacker-controlled data) can replay the exact `raw_body` + `hmac-sha256` header, while substituting the `shop-domain` header to name a victim shop. `Utils::HmacValidator.validate` still returns true because it revalidates only the body against the shared secret [6](#0-5) . `Registry.process` then calls the handler with `WebhookMetadata.new(... shop: request.shop ...)` where `shop` is the attacker-supplied header value, not the shop that actually generated the payload [4](#0-3) .

### Impact Explanation
Any app built on this gem that uses the `shop` field from `WebhookMetadata` to route, persist, or authorize per-tenant side effects (a documented and expected usage pattern) can be made to apply data or trigger actions attributed to a victim shop chosen by the attacker, using content the attacker fully controls. This is a cross-tenant identity confusion rooted directly in the gem's webhook verification code, matching the report's bug class of "a field acted on but not covered by the HMAC."

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on any shop the attacker controls (or otherwise observing one valid webhook delivery) to obtain a valid `(body, hmac)` pair, and (2) sending an HTTP POST to the app's public webhook endpoint with that body/HMAC and a forged `shop-domain` header. No access token, `client_secret`, or privileged access is required, since HMAC validation never inspects the header values.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable representation, or otherwise cryptographically bind them to the verified body (e.g., verify the shop against a store of known-installed shops with matching webhook registration) before constructing `WebhookMetadata` and invoking the handler. At minimum, `Request#to_signable_string` should not silently ignore fields (`shop`, `topic`) that downstream code treats as trusted.

### Proof of Concept
```ruby
# Attacker owns shop-a.myshopify.com and has the app installed there.
# Step 1: Attacker triggers an event on their own shop and captures the raw webhook POST:
#   body    = '{"id":1,"note":"attacker-controlled content"}'
#   headers include: "x-shopify-hmac-sha256" => <valid HMAC of body with the app's shared secret>
#                     "x-shopify-shop-domain" => "shop-a.myshopify.com"
#                     "x-shopify-topic"       => "orders/create"

# Step 2: Attacker replays the identical body/HMAC to the app's webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac,       # unchanged, still valid for `body`
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds (only body is checked),
# and the registered handler is invoked with
# WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker_json, ...)
```

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
