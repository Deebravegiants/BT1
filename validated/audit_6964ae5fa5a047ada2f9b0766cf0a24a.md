### Title
Webhook `shop` (and `topic`/`webhook_id`) attribution is not covered by the HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values that `ShopifyAPI::Webhooks::Registry.process` hands to the app's handler are read from unauthenticated HTTP headers that are never included in the signed data.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` verifies the HMAC purely against that signable string [2](#0-1) . Meanwhile `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all derived from the `shopify-shop-domain`/`shopify-topic`/etc. HTTP headers, which are completely outside the HMAC digest [3](#0-2) .

`Registry.process` validates the HMAC (over the body only) and then trusts `request.shop` and `request.topic` unconditionally to build the `WebhookMetadata` passed to the app's handler [4](#0-3) . `WebhookMetadata#shop` and `#topic` are plain `String` fields with no further binding to the signed payload [5](#0-4) .

The equality that should hold is: `shop-that-signed-the-body == shop-attributed-to-the-handler`. Because the HMAC only binds the byte content of the body, not the shop-domain header, this equality is not enforced by the library — any request whose body produces a valid HMAC (computed with the app's shared `api_secret_key`, which is identical for every shop that installs the app) can be delivered with an arbitrary `shopify-shop-domain` header, and the handler will process it under that spoofed shop identity.

An unprivileged attacker who installs the target app on their own (attacker-controlled) shop can trigger any webhook topic they like (e.g. by performing normal, benign actions such as creating a product/order on their own store). Shopify will deliver a body + valid HMAC (signed with the app's `api_secret_key`) to the app's webhook endpoint. The attacker — who fully controls the delivery destination behavior only in the sense of being able to replay the exact same authenticated bytes — can resend that identical `raw_body`/`hmac-sha256` pair to the same endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header to name a different, victim shop. `HmacValidator.validate` still passes because it never inspects those headers, and `Registry.process` will invoke the handler with `WebhookMetadata(shop: <victim-shop>, topic: ..., body: <attacker's own event payload>)`.

This breaks the tenant boundary the library is supposed to guarantee to consuming applications: apps are documented to trust `data.shop` from a processed webhook as the shop the event actually belongs to (see the "Register a Webhook for a Shop"/"Process a Webhook" docs flow), but the gem provides no cryptographic binding between the signed body and the shop attribution.

### Impact Explanation
This is a cross-tenant integrity issue: an attacker who is a legitimate (but unprivileged, arbitrary) merchant/app-installer can cause the consuming application to process attacker-controlled webhook data under a different, victim merchant's identity. Depending on how the host app uses `WebhookMetadata#shop` (e.g., looking up the victim's stored access token/session by `shop`, writing attacker data into the victim's records, or triggering shop-scoped side effects), this can lead to cross-tenant data corruption or actions being taken against a shop that never sent the corresponding data. This matches the "cross-tenant access" critical impact category, since the shop-scoping guarantee that host apps rely on when calling `ShopifyAPI::Webhooks::Registry.process` is not actually enforced by the gem.

### Likelihood Explanation
Likelihood is meaningful but requires two things: (1) the attacker must be able to install the app on a shop they control (a normal unprivileged action for any merchant/app-installer), and (2) they must be able to capture and replay a valid body+HMAC pair to the app's public webhook endpoint with a modified `shop-domain` header — which is straightforward once the raw bytes are known, since the gem's own header-normalization logic in `Request#initialize` accepts headers as a caller-supplied hash with no origin/IP or shop-consistency check [6](#0-5) .

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed body — for example, by having `to_signable_string` incorporate the `shopify-shop-domain` header (mirroring how `AuthQuery#to_signable_string` folds `shop`, `host`, etc. into the signed string [7](#0-6) ), or require host applications to independently verify that `request.shop` matches an expected/registered shop before trusting `WebhookMetadata#shop`. At minimum, document prominently that `Request#shop`/`#topic` are unauthenticated header values not covered by the HMAC so integrators don't assume tenant isolation is guaranteed by `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook-eligible event (e.g., `orders/create`) on their own data.
2. Shopify delivers to the app's webhook endpoint: `raw_body = '{"id":1,...attacker-controlled JSON...}'`, header `shopify-hmac-sha256 = Base64(HMAC-SHA256(api_secret_key, raw_body))`, header `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this exact `raw_body` + `shopify-hmac-sha256` value and re-sends it to the same endpoint, changing only `shopify-shop-domain: victim-shop.myshopify.com` (and optionally `shopify-topic`/`shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, raw_body)` and compares against the (unchanged) signature — validation succeeds because the header was never part of `to_signable_string` [8](#0-7) .
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` [9](#0-8) , causing the host application to process attacker-controlled data as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
