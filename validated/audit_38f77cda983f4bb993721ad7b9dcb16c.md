I have sufficient evidence to confirm the analog. The HMAC signature computed by `Utils::HmacValidator.validate` over `Webhooks::Request#to_signable_string` covers only the raw body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields (read from unauthenticated HTTP headers) are passed downstream to the webhook handler without being bound to that signature.

### Title
Webhook shop/topic identity not covered by HMAC signature enables cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable payload as the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from attacker-controllable HTTP headers and are never part of the signed data. `Registry.process` validates the HMAC over the body and then trusts these unauthenticated header fields to build the `WebhookMetadata` passed to the host app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors read straight from the (attacker-supplied) HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) .

`Registry.process` validates only that the body's HMAC is correct, then immediately forwards the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` values into `WebhookMetadata` given to the application's handler: [3](#0-2) .

The identity binding broken is: `shop the HMAC authenticates == shop attributed to the webhook event`. Since `ShopifyAPI::Context.api_secret_key` is a single app-level secret shared across every shop/tenant that installs the app (not a per-shop secret), any tenant that can obtain one validly-signed body/HMAC pair (e.g., by triggering a webhook on their own store, or by knowing the shared secret through other means available to an unprivileged tenant of the same app) can freely swap the `x-shopify-shop-domain` (and `topic`/`webhook_id`) headers to any value while keeping the same body+HMAC. `HmacValidator.validate` will still return true because the signature only ever covered the body: [4](#0-3) . The gem then hands the forged `shop` value to the host application as if it were an authenticated fact.

### Impact Explanation
This lets one tenant of a multi-tenant app spoof webhook events as originating from a different shop/tenant, because the `shop` field the application logic keys off of (`WebhookMetadata#shop`) is never actually authenticated — only the body bytes are. Host applications commonly use `shop` from webhook metadata to look up/act on that tenant's data (e.g., updating records, revoking access, replaying business events) since the library presents it as verified. This is a cross-tenant boundary violation reachable by any party able to produce one valid signed webhook body for the app (any installed/unprivileged tenant), matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high: exploitation requires only a single valid (body, HMAC) pair signed with the app's shared secret — which any tenant naturally receives from Shopify for their own legitimate webhook traffic — plus the ability to replay that body with modified headers to the app's webhook endpoint. No access token, `client_secret`, or privileged account is required; a normal, currently-installed unprivileged merchant can capture their own legitimate webhook delivery and replay it with a forged `shop-domain` header.

### Recommendation
Include the security-relevant identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content, or otherwise cryptographically bind them to the HMAC (e.g., validate signature over header+body concatenation, or require the app to independently verify `shop` against a known/registered value rather than trusting the header). At minimum, document clearly that `WebhookMetadata#shop`/`#topic` are NOT covered by the HMAC and must not be trusted as tenant identifiers without additional verification.

### Proof of Concept
1. Tenant A (attacker, running shop `attacker.myshopify.com`) receives a legitimate webhook delivery from Shopify for their own shop, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker replays the exact same body `B` and HMAC header `H` to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`).
3. `Webhooks::Request.new(raw_body: B, headers: forged_headers)` parses successfully since header presence checks don't validate correlation with the HMAC: [5](#0-4) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` — unaffected by the header change: [6](#0-5) .
5. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, and the host application processes the event as if it genuinely originated from `victim.myshopify.com`, even though it was forged by tenant A.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
