Found it. The `Webhooks::Request` (`lib/shopify_api/webhooks/request.rb`) exposes the identity binding gap the report's bug-class maps to: the `shop` field used by the app to route webhook data is **not covered by the HMAC**.

## Title
Webhook `shop` header is trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop` from the `X-Shopify-Shop-Domain` HTTP header [1](#0-0) , but `to_signable_string` (the data the HMAC is computed over) is only the raw request body [2](#0-1) . `Registry.process` validates the HMAC over that signable string and, if valid, passes `request.shop` straight into the handler's `WebhookMetadata` unchecked [3](#0-2) .

### Finding Description
The binding that should hold is: `shop-authenticated-by-HMAC == shop-delivered-to-handler`. Here, the HMAC (`X-Shopify-Hmac-Sha256`) only authenticates the JSON body bytes — it never binds the `X-Shopify-Shop-Domain` header value. `Utils::HmacValidator.validate` recomputes the signature purely from `verifiable_query.to_signable_string`, which for `Webhooks::Request` is `@raw_body` alone [4](#0-3) [2](#0-1) . Since a legitimate webhook payload/HMAC pair for shop A is valid regardless of what shop header accompanies it, an unprivileged actor who has observed (or replays) one valid `(body, hmac)` pair from Shopify for their own store can pair it with an arbitrary `X-Shopify-Shop-Domain` value, and `Registry.process` will accept it — `Utils::HmacValidator.validate(request)` returns true since only the body is checked — then hand the attacker-chosen `shop` to the app's webhook handler [3](#0-2) .

This is the same class of defect as the report's core lesson: an attacker-controlled field (here, the shop header) is acted upon by the application (routing/tenant-scoping webhook data) while not being cryptographically bound to the value that was actually authenticated (the body).

### Impact Explanation
This directly enables cross-tenant confusion in host applications that trust `WebhookMetadata#shop` (as returned by this gem) to scope data writes/reads per-tenant, since the gem provides and validates this field as if it were authenticated. An attacker who owns/controls one shop (a normal unprivileged Shopify merchant, or anyone able to trigger a webhook for their own store) can cause the target app to process/store webhook data under a different, arbitrary shop identifier that was never actually verified by Shopify's signature — a cross-tenant access primitive, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to have one genuine `(raw_body, hmac)` pair signed with the app's `client_secret` for any shop (e.g., from their own installed store's webhook deliveries, which they can observe as the recipient of their own webhooks), and the ability to send an HTTP POST to the app's configured webhook endpoint with a forged `shop-domain` header — no `client_secret`, access token, or privileged account needed. This is realistic for any merchant/store owner using the app.

### Recommendation
Include the shop domain (and other headers/claims the app relies on for tenant identity, such as `topic`, `api-version`) in the value covered by the HMAC verification — i.e., have `Webhooks::Request#to_signable_string` incorporate the shop header, or independently authenticate the shop against the raw-body-based HMAC only when combined with a canonical representation that includes the shop, so any mismatch invalidates the signature. Since Shopify's actual webhook HMAC scheme is computed over the raw body only, the gem should instead avoid exposing an unauthenticated `shop` field on `Request` as if it were trustworthy, or explicitly document/require correlation with a separately verified value (e.g., matching against a known active session for the shop) before it is used for tenant-scoping decisions.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and observes one legitimate webhook delivery: raw body `B` and its valid `X-Shopify-Hmac-Sha256` value `H` (computed by Shopify over `B` using the app's shared secret).
2. Attacker replays a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` object [5](#0-4) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes the HMAC over `B` [6](#0-5) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though nothing verified by Shopify's signature ties this webhook to that shop [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
