### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The `notifyRewardAmount` report is a case where a value used to drive downstream accounting (`rewardData.rate`) is derived without being fully bound to the value that was actually authorized/verified (`amount`), causing a mismatch between what was checked and what was acted upon. The closest analog in this Ruby gem is in `ShopifyAPI::Webhooks::Request`/`ShopifyAPI::Webhooks::Registry`, where the `shop` (tenant identity) field that a consuming app relies on for routing/authorization is never included in the HMAC signature that this gem validates — the HMAC only covers the raw body bytes, while `shop`, `topic`, `webhook_id`, and `api_version` are parsed from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `hmac` is read from the `hmac-sha256` header [2](#0-1) . `Registry.process` verifies this HMAC using `Utils::HmacValidator.validate(request)` [3](#0-2) , which in turn calls `validate_signature`, comparing a signature computed only over `verifiable_query.to_signable_string` (i.e., the raw body) against the received HMAC [4](#0-3) .

However, `request.shop`, `request.topic`, and `request.webhook_id` are all pulled from separate, unauthenticated headers (`shop-domain`, `topic`, `webhook-id`) [5](#0-4) , and after HMAC validation succeeds, `Registry.process` passes `request.shop` directly into `WebhookMetadata` given to the consuming app's handler as the tenant identity [6](#0-5) .

The identity-binding equality that should hold is:
`bytes_covered_by_HMAC == bytes_used_to_authenticate/route_the_request`

In reality: `bytes_covered_by_HMAC (raw_body only) ≠ bytes_used_to_route (shop-domain header, topic header, webhook-id header)`.

Because Shopify signs webhooks per-app (not per-shop) using the single `Context.api_secret_key`, any shop that is a genuine, unprivileged merchant/user of the app receives real webhooks with a valid HMAC over some raw body. That same attacker-controlled shop can capture a legitimate `(raw_body, hmac)` pair from their own store's webhook deliveries and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will hand the (forged) victim `shop` value to the app's handler as if the event genuinely originated from that shop.

### Impact Explanation
This breaks the tenant-identity binding that a multi-tenant Shopify app is expected to rely on when processing webhooks — the gem provides `request.shop` to app handlers as a trusted, HMAC-verified value, but it is not actually covered by the signature. An attacker who is a legitimate (even unprivileged) merchant installing the app can forge webhook events attributed to another tenant, causing the app to execute business logic (data writes, cache invalidation, resource sync/deletion, notification delivery, etc.) against a shop the attacker does not own. This is a cross-tenant access issue as defined in scope (Critical).

### Likelihood Explanation
Requires only that the attacker (1) install the app on their own shop to receive at least one genuine webhook delivery with a valid HMAC, and (2) be able to send an HTTP request to the app's webhook endpoint with a modified `x-shopify-shop-domain` header (or the legacy `shopify-shop-domain` variant) while keeping the original body/HMAC pair — no access to `api_secret_key`, access tokens, or any privileged Shopify state is needed. The gem's own header handling explicitly supports both `x-shopify-*` and `shopify-*` header name variants [7](#0-6) , so no special knowledge of internal formats is required.

### Recommendation
Include the tenant/routing identity fields (`shop-domain`, and ideally `topic`/`webhook-id`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., by validating that the shop/topic asserted in the headers matches metadata embedded in, or otherwise provably tied to, the signed payload). At minimum, document prominently that `request.shop` is derived from an unauthenticated header and must not be trusted as a verified tenant identifier by consuming applications, and consider providing a variant of `Request`/`Registry.process` that fails closed unless the shop can be independently corroborated (e.g., against an active `Session` already known for that topic/webhook subscription).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets Shopify deliver a real webhook (e.g., `orders/create`) to the app's webhook endpoint, capturing the raw JSON body and its `x-shopify-hmac-sha256` value.
2. Attacker (or any actor who can reach the app's public webhook endpoint) replays the exact same `raw_body` and `x-shopify-hmac-sha256` header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers normally [8](#0-7) , and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the unmodified HMAC [3](#0-2) .
4. The app's registered handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` [9](#0-8) , even though the event never originated from that shop — demonstrating the cross-tenant identity confusion.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-59)
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
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L192-199)
```ruby
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
