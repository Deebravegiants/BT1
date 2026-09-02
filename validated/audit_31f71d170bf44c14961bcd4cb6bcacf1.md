This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#hmac` validation covers only `@raw_body` via `to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`), while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:20-33`). The `Registry.process` method (`lib/shopify_api/webhooks/registry.rb:189-199` shown earlier) validates the HMAC and then trusts `request.shop` and `request.topic` from those same unauthenticated headers when dispatching to the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`. This breaks the identity binding: `shop authenticated ≠ shop delivered to handler`, since the HMAC signature never covers the shop-domain header.

### Title
Webhook shop/topic identity spoofing via unauthenticated headers not covered by HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `api_version`, and `webhook_id` values used by `Registry.process` to attribute and dispatch the webhook are read straight from HTTP headers that are never included in the signed payload.

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the `hmac` value using `OpenSSL.secure_compare` [1](#0-0) .
For webhooks, `to_signable_string` is defined to return only `@raw_body` [2](#0-1) .
Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from the `x-shopify-*`/`shopify-*` HTTP headers, none of which are part of the signed bytes [3](#0-2) .
`Registry.process` validates the HMAC and then immediately trusts those header-derived fields to route and label the webhook, passing `request.shop` straight into the handler's `WebhookMetadata` [4](#0-3) .

The equality that should hold is: **bytes verified by HMAC == identity fields (shop, topic) acted upon by the handler**. Here the gem only enforces "body bytes are authentic," but silently allows "shop-domain header can be anything the caller sets," because the header is parsed but never bound into the signable string. Any caller who can produce one valid `(raw_body, hmac)` pair signed with the app's secret — e.g., by capturing/replaying a single legitimate webhook delivery from any shop (including the attacker's own shop, or one they can trigger, such as `orders/create` from a store they control) — can resend that exact body with a forged `shopify-shop-domain` header pointing at a victim shop, and the HMAC check still passes because the signature never covered the shop header.

### Impact Explanation
This is a cross-tenant identity confusion: a webhook payload that was legitimately signed for shop A can be relabeled and processed by the app as if it belongs to shop B, since `WebhookMetadata.shop` is taken verbatim from the unauthenticated header. Depending on how the host application's handler trusts `data.shop` (e.g., to look up records, write GDPR redaction data, or scope database writes), this can lead to cross-tenant data corruption or disclosure attributed to the wrong merchant — a Critical-tier cross-tenant access issue per the same-secret HMAC design (all shops using an app share the same `api_secret_key`, so any shop installer can forge a valid `(body, hmac)` pair for their own traffic and relabel it as another shop's).

### Likelihood Explanation
Any merchant that has installed the app (and thus can trigger at least one legitimate webhook delivery for their own shop) possesses a valid `(raw_body, hmac)` pair signed with the shared `api_secret_key`. They can then replay that exact body to the app's webhook endpoint with an arbitrary `shopify-shop-domain`/`shopify-topic` header, and `Utils::HmacValidator.validate` will accept it because the signature check never covers the headers. No access to the app's `client_secret` or another merchant's credentials is required beyond having any one valid signed webhook.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signable payload — or otherwise cryptographically bind the shop/topic used for dispatch to the same bytes that were HMAC-verified — instead of trusting them from unauthenticated headers after only the body is verified.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com` with body `{"id":1}` and header `shopify-hmac-sha256: <valid-hmac-of-body>`.
2. Attacker captures/replays this exact `(body, hmac)` pair to the app's webhook endpoint, but changes the header to `shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `shopify-topic`).
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `@raw_body` against the HMAC [6](#0-5) .
5. The handler receives `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with `shop` = `victim-shop.myshopify.com`, even though the signed body was never associated with that shop [7](#0-6) .

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
