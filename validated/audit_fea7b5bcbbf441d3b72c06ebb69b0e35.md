This confirms the vulnerability: the webhook HMAC only covers `@raw_body` (the JSON body), while `shop`, `topic`, and `webhook_id` are read directly from HTTP headers that are never included in `to_signable_string`, per `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`'s `process` method which dispatches based on `request.shop`/`request.topic` after only validating the body HMAC.

### Title
Webhook `shop` and `topic` identity are not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw request body only [1](#0-0) , while the `shop`, `topic`, and `webhook_id` values used by the registry to route and attribute the webhook are read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC of the request and then dispatches the handler using `request.shop` and `request.topic` taken from those unverified headers [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop header == shop that produced/authorized this signed payload`. Instead, `HmacValidator.validate` only checks `OpenSSL.secure_compare(computed_signature, received_signature)` where `computed_signature` is derived solely from `to_signable_string`, i.e., the raw JSON body [4](#0-3) . The `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers are never part of the signed material [5](#0-4) .

Because the shared secret (`api_secret_key`) is common to the whole app across all of its installed shops (multi-tenant), any unprivileged internet user who owns/operates their own Shopify development store that has this same app installed can trigger a legitimate webhook for their own shop, capturing a genuinely-signed `(raw_body, hmac)` pair. Since the signature covers only the body bytes and not the `shop-domain` header, that attacker can replay the identical body+HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and/or `shopify-topic`) with a victim shop's domain. `HmacValidator.validate` will still pass because the HMAC only vouches for the untouched body bytes, not for which shop or topic they belong to. `Registry.process` then invokes the handler with `WebhookMetadata` attributing the (attacker-controlled) body to the victim shop [6](#0-5) , since nothing re-derives or cross-checks shop identity against the signed content.

This breaks the "bytes verified versus bytes parsed" pattern from the prompt rules: the bytes verified by HMAC are the JSON body only; the bytes parsed and acted upon for tenant attribution (`shop`, `topic`, `webhook_id`) are unauthenticated header bytes.

### Impact Explanation
This enables cross-tenant confusion in the app's webhook handling: an attacker-controlled but validly-HMAC'd webhook payload (from the attacker's own shop) can be attributed to an arbitrary victim `shop` value inside `WebhookMetadata`, which app developers use as the trust anchor for looking up sessions/records keyed by shop and acting on data "from" that shop (e.g. mandatory GDPR webhooks `shop/redact`, `customers/redact`, `customers/data_request`, or app-specific data-sync handlers). Depending on how the host app trusts `WebhookMetadata#shop`, this can lead to processing/state changes against the wrong tenant's records — a cross-tenant access impact.

### Likelihood Explanation
Requires only that the attacker run their own Shopify store with the target app installed (an unprivileged actor relative to other tenants), replay a captured request to the app's public webhook endpoint with a modified `shop-domain` header, and rely on the app trusting `WebhookMetadata#shop` — a documented, standard usage pattern for this gem. No access token, `client_secret`, or privileged credential is needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (or otherwise cryptographically bind them, e.g., via a MAC over `header-values || body`), so that any mutation of the shop/topic headers invalidates the signature. At minimum, document/enforce that `WebhookMetadata#shop` must never be trusted as an authenticated tenant identifier without additional binding.

### Proof of Concept
1. Attacker's own store (App installed) triggers a real webhook event, e.g. `orders/create`; Shopify sends: body `B`, headers `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: orders/create`, `shopify-hmac-sha256: H` where `H = Base64(HMAC-SHA256(secret, B))`.
2. Attacker intercepts/replays this request to the same app endpoint, but resends it with `shopify-shop-domain: victim-shop.myshopify.com` (topic/webhook-id may also be altered), keeping body `B` and header `H` unchanged.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers)` is constructed; `HmacValidator.validate(request)` recomputes HMAC over `B` only and it matches `H`, so validation succeeds — see [7](#0-6) .
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [6](#0-5) , causing the app to act on attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
