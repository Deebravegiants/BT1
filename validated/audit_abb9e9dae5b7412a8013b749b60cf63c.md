### Title
Webhook shop-domain identity not covered by HMAC, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw request body, while the `shop` (tenant identity) that the webhook is attributed to comes from an unsigned header. Any party that can obtain one valid `(body, hmac)` pair for the shared app secret can relabel the webhook to any other shop and have it processed as if it originated from that shop's data.

### Finding Description
`Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` to build the signed payload: [1](#0-0) 

`Webhooks::Request#to_signable_string` returns only the raw body — no shop, topic, or webhook-id data is included in the signed content: [2](#0-1) 

The `shop` attribute, however, comes straight from the unauthenticated `shopify-shop-domain` header: [3](#0-2) 

`Registry.process` then forwards this unverified `shop` value straight into `WebhookMetadata`, which the host application's handler uses to attribute the payload to a tenant: [1](#0-0) [4](#0-3) 

`HmacValidator.validate` itself only checks the HMAC computed from `to_signable_string` against `Context.api_secret_key` (the single secret shared by the app across *all* of its installed shops, not a per-shop secret): [5](#0-4) 

**Binding that should hold but doesn't:**
`shop_header_used_by_handler == shop_that_the_HMAC_secret_holder_intended_for_this_body`

Because the same `api_secret_key` is used to validate webhooks for every shop that has installed the app, and the shop identity is carried outside the signed content, this equality is not enforced. A request with a body+HMAC pair that was legitimately generated for Shop A's webhook can be replayed with the `shop-domain` header rewritten to Shop B, and it still passes `HmacValidator.validate` because that function never inspects the header.

### Impact Explanation
This breaks the tenant-isolation guarantee that host applications rely on when they key their per-shop data (sessions, order records, customer PII, redaction/compliance actions) by the `shop` value handed to them by `WebhookMetadata`. An attacker who is a genuine merchant using the same app (so they receive real, validly-signed webhook deliveries for their own shop) can capture a `(raw_body, hmac)` pair from their own webhook traffic and replay it directly to the app's public webhook endpoint with the `x-shopify-shop-domain` header swapped to a victim shop's domain. The forged webhook is accepted (HMAC validates), and the handler processes attacker-controlled body content attributed to the victim shop — a cross-tenant data-integrity/data-injection issue (e.g., forging `customers/redact`, `orders/create`, `app/uninstalled`, etc. against a shop the attacker does not own). Because this is a direct cross-tenant boundary crossing enabled by identity data traveling outside the signed content, it meets the "cross-tenant access" Critical bar.

### Likelihood Explanation
Exploitation requires only unprivileged access to the app as a normal merchant/installer (to obtain one legitimate `(body, hmac)` sample) plus the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers — both trivially available to any internet user with no special privileges, no leaked secrets, and no social engineering. The victim shop does not need to be the attacker's own; any shop domain string can be substituted since it is never checked against the signed content.

### Recommendation
Bind the tenant identity into the signed content, or otherwise cryptographically tie the `shop-domain` header to the HMAC:
- Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification (this deviates from Shopify's wire format, so alternatively:
- Require host applications/`Registry.process` to cross-check that `request.shop` matches an actual installed/session shop known to the app before dispatching to the handler, rejecting webhooks for shops with no active session/install.
- At minimum, document prominently that `shop-domain` is not authenticated by the HMAC and that consuming code must independently verify the shop is a legitimate, currently-installed tenant before trusting the payload.

### Proof of Concept
1. App merchant "Attacker Shop" (`attacker.myshopify.com`) has the app installed and legitimately receives a real webhook delivery, e.g. an `orders/create` webhook with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this HMAC is valid because `Context.api_secret_key` is the same secret used for every shop's webhooks, per `HmacValidator.validate_signature`: [6](#0-5) 
2. Attacker crafts a raw POST to the app's public webhook endpoint using the exact captured body `B` and HMAC header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`.
3. `Webhooks::Request.new` parses these headers without validating that `shop` corresponds to the shop that produced `B`/`H`: [7](#0-6) 
4. `Registry.process` calls `HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` with the shared secret, never inspecting the shop header: [8](#0-7) 
5. The registered handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and the host application processes it as authentic data belonging to `victim-shop.myshopify.com`, even though `victim-shop.myshopify.com` never sent this webhook and possibly never triggered event `B` at all.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
