This confirms the finding: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC-over-body via `HmacValidator.validate(request)` and then dispatches the handler using `request.shop` as the tenant identity, with no binding between the verified bytes and that header [3](#0-2) .

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body [1](#0-0) , but `Registry.process` trusts the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header as the tenant identity passed to the app's webhook handler [3](#0-2) . This breaks the identity binding: `verified(bytes) == raw_body`, but `acted_on(shop) == header["shop-domain"]`, and the header is never part of `verified(bytes)`.

### Finding Description
`Utils::HmacValidator.validate` recomputes an HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field via `OpenSSL.secure_compare` [4](#0-3) . For webhook requests, `to_signable_string` is exactly `@raw_body` [1](#0-0) ; the `shop`, `topic`, and `webhook_id` accessors instead read directly from HTTP headers with no cryptographic linkage to the signed body [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the registered handler [3](#0-2) . Since a valid signature only proves the body was HMAC'd with the app's secret — it says nothing about which shop the header claims to be from — any request bearing a body/HMAC pair that is valid for the app's secret (e.g., one legitimately captured from a webhook delivered to the attacker's own store, where the attacker is a genuine merchant with the app installed) can be replayed to the app's shared webhook endpoint with an arbitrary, attacker-chosen `shop-domain` header. The handler receives `WebhookMetadata` claiming to be from a different, victim tenant, while the verified bytes never bound the shop at all.

### Impact Explanation
Multi-tenant apps typically key webhook processing (order/customer/GDPR data updates, feature toggles, uninstall handling, etc.) by `WebhookMetadata#shop`. Because that field is unauthenticated relative to the HMAC, an attacker who controls one legitimate installation of the app (their own shop) can forge cross-tenant webhook deliveries attributed to any other shop domain, without ever needing the app's `api_secret_key` or any victim credentials. This matches the "Critical - cross-tenant access" category, since it lets one tenant inject data/events that the app attributes to another tenant.

### Likelihood Explanation
Any developer/merchant who has installed the app on their own store can capture a legitimate webhook delivery for that store (body + HMAC, which is validly signed by Shopify using the app's real secret) and replay it to the app's public webhook endpoint with a modified `X-Shopify-Shop-Domain` header. No secret material, victim access, or privileged position is required — only the ability to send an HTTP request to the app's already-public webhook URL, which is the intended entry point for this code path (`Registry.process`).

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that's actually verified, or otherwise cryptographically tie the header claims to the signed payload. Options:
- Have the app-level webhook endpoint associate each accepted webhook only with the shop that is independently known to be currently registered for that specific `webhook_id`/subscription (looked up server-side, not trusted from the header) before dispatching.
- At minimum, document prominently that `Request#shop`/`#topic` are unauthenticated and that host applications must not use them as an authorization/tenant boundary without independent verification (e.g., cross-checking against the app's own webhook subscription records for the given `webhook_id`).

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and receives (or triggers, e.g., by placing an order) a legitimate webhook POST to the app's shared endpoint, including a correctly-signed `X-Shopify-Hmac-Sha256` header and body.
2. Attacker replays the exact same body and HMAC header to the same endpoint, but replaces `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Webhooks::Request.new` accepts the request (all required headers present) [5](#0-4) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body/HMAC pair, both of which are unchanged and genuinely valid for the app's secret [6](#0-5) .
4. The registered handler is invoked with `WebhookMetadata` reporting `shop: "victim.myshopify.com"` [7](#0-6) , causing the app to process attacker-supplied data as if it originated from the victim tenant.

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
