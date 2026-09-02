### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are trusted from unauthenticated headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  so `Utils::HmacValidator.validate` authenticates the body bytes alone [2](#0-1) . However, `Registry.process` reads `request.topic`, `request.shop`, `request.webhook_id`, and `request.api_version` straight from the (unauthenticated) headers and forwards them as trusted tenant/context identity to the app's handler [3](#0-2) , and `Request` pulls these directly from HTTP headers with no cross-check against the signed body [4](#0-3) .

### Finding Description
The identity binding broken here is:
`HMAC-covered bytes (raw_body only)` ≠ `fields acted upon (shop, topic, webhook_id, api_version headers)`.

Because `to_signable_string` is defined as just `@raw_body`, verifying the HMAC proves only "this exact JSON body was signed with the app's secret key at some point by Shopify," it proves nothing about which shop, topic, or webhook id the body is associated with — those come from separate, unsigned HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`) [5](#0-4) .

An unprivileged internet user who operates their own shop installed on the app receives genuine webhook deliveries for their own store, each with a valid `raw_body` + `hmac` pair (Shopify signs these using the app's shared secret, and the attacker's own webhooks are legitimately signed). That attacker can then replay the exact same `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `shop-domain` (and/or `topic`/`webhook_id`) header for a different, victim shop. `Registry.process` will find `Utils::HmacValidator.validate(request)` still succeeds — since it only checks the body — and will dispatch the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [3](#0-2) , attributing attacker-controlled body content to a shop the attacker does not own. Any app logic that keys tenant-scoped state (order records, inventory sync, entitlement flags, deduplication by `webhook_id`, etc.) off `data.shop`/`data.topic`/`data.webhook_id` as documented in `docs/usage/webhooks.md` [6](#0-5)  will process this as an authentic event for the impersonated shop.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate (even unprivileged) merchant of the app can forge webhook deliveries falsely attributed to any other shop by controlling only the unauthenticated header set, while reusing a validly-signed body they legitimately received for their own store. This matches the Critical bucket "cross-tenant access" since the app is given attacker-controlled `shop` context alongside a cryptographically-authenticated body, without any binding between the two.

### Likelihood Explanation
Requires the attacker to install (or otherwise operate) the app on at least one shop to obtain one legitimate `raw_body`/`hmac` pair — a normal, unprivileged action any merchant can take, not requiring the app's `api_secret_key`, a stolen access token, or social engineering. The replay itself is a single crafted HTTP request to the app's public webhook endpoint with modified headers.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-verified signable content (or independently bind them, e.g. by requiring the `shop` header to match a shop known to have an active webhook subscription with the given `webhook_id`) so that the HMAC also authenticates the identity fields being acted upon, not merely the JSON payload bytes.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate `orders/create` webhook: `raw_body = B`, headers include `x-shopify-hmac-sha256: H` (valid for `B`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body = B` and `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or a chosen `x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully [7](#0-6) ; `Utils::HmacValidator.validate` returns `true` because it only re-computes HMAC over `B` [2](#0-1) .
4. `Registry.process` calls the app's handler with `WebhookMetadata` reporting `shop: "victim-shop.myshopify.com"` [8](#0-7) , causing the app to act on data for a tenant the attacker does not control.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
