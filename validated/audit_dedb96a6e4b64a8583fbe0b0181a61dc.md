### Title
Webhook `shop` domain claim is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an unauthenticated HTTP header, while the HMAC signature it validates against only covers the raw request body. This breaks the intended binding `shop_verified == shop_acted_on`, mirroring the report's root cause where the value trusted for accounting (`d_reward`) was not the same value that was actually verified/attributed. Here, the identity attribute (`shop`) used by `Registry.process` to build `WebhookMetadata` and dispatch to the app's handler is never included in the signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` fields are all parsed straight from HTTP headers, independent of the HMAC computation: [2](#0-1)  and the header extraction/normalization logic that accepts arbitrary caller-supplied header hashes: [3](#0-2) .

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only recomputes the signature over `to_signable_string` (i.e., the body) and compares it to the `hmac` header, then immediately trusts `request.shop` to construct the tenant-scoped `WebhookMetadata` passed to the app's handler: [4](#0-3) . `HmacValidator.validate`/`validate_signature` never reference `shop` at all: [5](#0-4) .

Binding that should hold but doesn't:
`shop_bytes_verified_by_HMAC == shop_bytes_acted_on_by_handler`

Before request: HMAC is computed by Shopify over `(body)` only for a specific installed shop's event.
After an attacker-controlled replay: the same valid `(body, hmac)` pair is submitted with a different `shop-domain` header value. `HmacValidator.validate` still returns `true` (it never inspected `shop`), and `Registry.process` builds `WebhookMetadata` with the attacker-chosen `shop`, dispatching to the host app's handler as if the event genuinely originated from that shop — a cross-tenant identity spoof enabled entirely inside this gem's verification/dispatch path.

Because Shopify webhook HMACs are computed with the app's single `client_secret` shared across all shops using the app (not a per-shop key), anyone who can obtain one legitimately-signed `(body, hmac)` pair — e.g., by installing the app on their own attacker-controlled shop and receiving a real webhook — possesses a signature that this gem will accept for that body regardless of which shop header accompanies it.

### Impact Explanation
This is a cross-tenant access vector: the gem's own HMAC-validation-and-dispatch pipeline accepts a body signature as proof of authenticity but attributes the event to an arbitrary attacker-supplied `shop`, which the host application uses (via `WebhookMetadata#shop`) as the tenant key for e.g. `shop/redact`, `customers/redact`, `customers/data_request`, or app-specific business webhooks (`Registry::MANDATORY_TOPICS`: [6](#0-5) ). An attacker who is a legitimate but unprivileged installer of the app (on their own shop) can trigger tenant-scoped side effects (e.g., forced data-redaction, forged order/customer events) against a victim shop that never sent that request.

### Likelihood Explanation
Requires only: (1) installing the target app on an attacker-controlled shop to obtain one validly signed webhook body/HMAC pair (a normal, unprivileged action), and (2) sending a crafted HTTP POST directly to the app's webhook endpoint with the captured body/HMAC and a spoofed `x-shopify-shop-domain`/`shopify-shop-domain` header. No access token, `client_secret`, or victim credentials are needed. This is entirely reachable through the gem's public `Webhooks::Request`/`Webhooks::Registry.process` API as documented for host apps to use.

### Recommendation
Bind the tenant/shop identity into the material that is cryptographically verified, or verify `shop` against an independent trust source before dispatch:
- Include `shop` (and ideally `topic`, `webhook_id`) in the signable string used for HMAC verification, or
- Require the host application/gem to cross-check `request.shop` against the shop of an already-established, previously authorized session/installation record before invoking the handler, rejecting webhooks for shops with no active session, and
- Document explicitly that `shop` is unauthenticated header data and must not be trusted as a tenant boundary without this additional check.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a real webhook (e.g. `orders/create`) delivered by Shopify with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker sends a direct HTTP POST to the app's webhook endpoint with the exact same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` parses headers, setting `shop` = `victim-shop.myshopify.com` while `to_signable_string` still returns `B`: [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and it matches `H` (valid), independent of the `shop` header: [8](#0-7) .
5. The handler is invoked with `WebhookMetadata.new(... , shop: "victim-shop.myshopify.com", ...)`, and the host application processes the event as an authentic action for the victim shop: [9](#0-8) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
