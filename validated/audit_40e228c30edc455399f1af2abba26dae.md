### Title
Webhook `shop-domain`, `topic`, `webhook-id` and `api-version` are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives its `shop`, `topic`, `webhook_id` and `api_version` from raw, unauthenticated HTTP headers, while `Utils::HmacValidator` only verifies the HMAC over the raw request body. This breaks the binding "bytes verified == bytes acted on": the identity of the tenant (`shop`) that a webhook payload is attributed to is never covered by the cryptographic signature, so an attacker who possesses one valid `(raw_body, hmac)` pair can replay it while freely rewriting the `shop-domain` header to any target shop.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via: [1](#0-0) 

`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string` to compute the HMAC: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns **only** `@raw_body` — none of the Shopify headers are folded into the signed string: [3](#0-2) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` — the values that `Registry.process` hands to the app's handler as the tenant/topic identity — are read straight from attacker-controllable headers with no cryptographic binding to the signed body: [4](#0-3) [5](#0-4) 

The equality that should hold is:
`bytes verified by HMAC == bytes the handler treats as authoritative for the tenant (shop) and event (topic/webhook_id)`

Instead, only `raw_body` is verified while `shop`, `topic`, `webhook_id`, `api_version` are parsed independently from headers and passed unchecked to `WebhookMetadata`, breaking the binding.

**Attack sequence:**
1. Attacker obtains a valid `(raw_body, hmac)` pair. This is trivial to get: register any free Shopify development store, install the same app instance (or a clone sharing the same `api_secret_key`/app), and capture one genuine webhook HTTP request Shopify sends to the app (e.g. `orders/create`, `customers/data_request`, or any topic the app is subscribed to). Because the app's `api_secret_key` is shared across all shops that install the app, this HMAC is valid for any body signed with that key, regardless of which shop originated it.
2. Attacker replays the exact same raw body and HMAC to the target app's webhook endpoint, but freely modifies the `x-shopify-shop-domain` header to the victim shop's domain (and/or `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version` headers).
3. `HmacValidator.validate` passes because it only checks `raw_body` against the (unchanged) HMAC.
4. `Registry.process` dispatches to the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop` is now the attacker-chosen victim domain, not the tenant that actually produced/authorized the signed payload.

### Impact Explanation
This is a cross-tenant identity-binding break: the app's webhook handler is told "this authentic, Shopify-signed payload belongs to shop X" when in fact shop X never sent or authorized it. Any host application logic that keys off `data.shop` to select which tenant's data/session to mutate (this is the intended and documented usage — see `WebhookController` example processing `ShopifyAPI::Webhooks::Registry.process`) can be tricked into applying an attacker-controlled but validly-HMAC'd body to a different tenant. Because the three GDPR/mandatory topics (`shop/redact`, `customers/redact`, `customers/data_request`) are always routed through this same `Request`/`Registry.process` path, an attacker can also spoof mandatory compliance webhooks against a victim shop's domain, or make `orders/create`-style payloads appear to originate from a shop they don't control. This matches "cross-tenant access" from a credential the attacker does hold (their own app installation/HMAC secret), i.e. High/Critical impact per the rubric.

### Likelihood Explanation
Requires only unauthenticated internet access and an app install the attacker legitimately controls (e.g., a free Shopify dev store using the same app), which is realistic for any public/multi-tenant Shopify app. No access token, `client_secret`, or privileged account of the *victim* is required — only a signed body that the attacker's own shop already received.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed string, or otherwise cryptographically bind them to the body (e.g., derive an expected shop from a separately-verified source, or require the host app to independently confirm `shop` against session/store data before trusting it). At minimum, document prominently that `Webhooks::Request#shop`/`#topic` are NOT covered by HMAC verification and must not be trusted for tenant identification without additional server-side checks.

### Proof of Concept
```ruby
require "shopify_api"

secret = ShopifyAPI::Context.api_secret_key
raw_body = '{"id":1,"note":"legit order for attacker-shop.myshopify.com"}'

hmac_digest = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
valid_hmac_b64 = Base64.encode64(hmac_digest) # this is genuinely computed by Shopify for attacker's own shop

# Attacker replays with a different shop-domain header - HMAC still validates
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- attacker-controlled, not covered by HMAC
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Passes: HmacValidator only checks raw_body against the signature
ShopifyAPI::Webhooks::Registry.process(request)
# => handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "orders/create", ...)
#    even though victim-shop never sent this payload.
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

**File:** lib/shopify_api/webhooks/request.rb (L188-199)
```ruby

```
