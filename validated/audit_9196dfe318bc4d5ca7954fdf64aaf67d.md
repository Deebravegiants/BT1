### Title
Webhook `shop`, `topic`, `webhook_id` and `api_version` fields are not covered by the HMAC signature, allowing tenant spoofing on replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values consumed by the webhook handler are read from HTTP headers that are never included in the signed content. This breaks the identity binding that should hold: `shop authenticated by HMAC == shop delivered to the handler`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all derived from unauthenticated headers: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` — i.e., only the body bytes: [3](#0-2) 

`Registry.process` accepts the request once the body HMAC checks out, then constructs `WebhookMetadata` directly from the unauthenticated header fields (`request.shop`, `request.topic`, `request.webhook_id`, `request.api_version`) and dispatches it to the app's handler: [4](#0-3) [5](#0-4) 

Contrast this with the OAuth callback path, where `HmacValidator.validate(auth_query)` verifies a signature computed over a query string that *does* include `shop` (see `AuthQuery#to_signable_string`) — the shop identity is bound to the signature there. No such binding exists for webhooks.

Because the app's `client_secret` (and hence the HMAC secret) is shared across every shop that installs the app, any merchant who installs the app on their own store is an "unprivileged internet user" with respect to other tenants of the same app, yet they legitimately receive real webhooks signed with the same secret. Such a user can capture a genuine `(raw_body, hmac)` pair delivered to their own endpoint for their own shop, then replay that exact body+HMAC pair to the app's webhook endpoint while substituting a different `shop-domain` (and/or `topic`/`webhook_id`/`api_version`) header value. Since the signature never covered the shop header, `HmacValidator.validate` still returns `true`, and `Registry.process` will hand the (attacker-controlled) `shop` value to the app's handler as if it were authenticated data for that shop.

### Impact Explanation
This crosses a tenant boundary that the gem is expected to enforce: the shop identifier delivered to the merchant's webhook handler is not actually authenticated by the HMAC, only the payload bytes are. An app that trusts `WebhookMetadata#shop` to select which tenant's session/access token to act on (a documented and expected usage pattern for this gem) can be made to process replayed/forged data under a victim shop's identity — cross-tenant confusion enabled purely by data the gem itself failed to bind to the signature.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled store (an ordinary, unprivileged action available to any Shopify merchant), (2) capturing one legitimately signed webhook delivered to that store, and (3) replaying the captured `raw_body`/`hmac` to the app's public webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or privileged account is required — only observation of traffic the attacker is entitled to receive for their own shop.

### Recommendation
Include the tenant/shop identity (and ideally topic, webhook id, and api version) inside the signed content verified by `HmacValidator`, or otherwise cryptographically bind the `shop-domain` header to the HMAC (e.g., by validating it out-of-band against the session/shop that requested the corresponding webhook registration) before constructing `WebhookMetadata`. At minimum, document that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be trusted as a tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and receives a genuine webhook at their configured endpoint with body `raw_body` and header `x-shopify-hmac-sha256: H` (valid for `app.client_secret`).
2. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256: H` to the same app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers [6](#0-5) , and `Registry.process` calls `HmacValidator.validate(request)`, which passes because the HMAC only ever covered `raw_body` [7](#0-6) .
4. The app's handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` and the attacker's chosen body, even though that body was never actually produced or signed for `victim-shop`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
