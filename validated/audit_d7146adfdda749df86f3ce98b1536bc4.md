This confirms the vulnerability. The `Registry.process` method validates only the HMAC over the raw body, while `shop`, `topic`, `webhook_id`, and `api_version` come from unsigned HTTP headers and are passed straight to the app's handler as trusted tenant identity.

### Title
Webhook shop-domain identity spoofing via unauthenticated header - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats `request.shop` (and `topic`/`webhook_id`/`api_version`) as authenticated tenant identity, but these values come from HTTP headers that are never included in the HMAC computation, allowing any holder of a validly-signed webhook body to relabel it as belonging to a different shop.

### Finding Description
The HMAC validation used to authenticate inbound webhooks only signs the raw request body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers, which are outside the signed data: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `to_signable_string`, i.e. the body only, and never incorporates the headers into the signature check: [3](#0-2) 

`Registry.process` then passes `request.shop` straight through to the app's `WebhookHandler` as trusted metadata, with no cross-check that the `shop` header matches any shop-specific value inside the signed body: [4](#0-3) [5](#0-4) 

Since the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that installs the app, a merchant who installs the app on their own store legitimately receives correctly-HMAC'd webhook deliveries for their own shop's events. That attacker can capture such a body+HMAC pair and resend it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header rewritten to name a **different, victim** shop. `Utils::HmacValidator.validate(request)` still succeeds because it only checks the body, and `Registry.process` hands the forged shop identity to the handler as authenticated fact. This breaks the identity binding: `shop header value == shop that actually produced/authorized the signed payload` is assumed true but is never enforced anywhere in this code path.

### Impact Explanation
This is cross-tenant identity spoofing at the webhook trust boundary: the receiving application's webhook handler (built per this gem's documented contract) makes shop-scoped decisions — e.g., looking up a merchant's session/access token, updating shop-specific records, or triggering redaction/GDPR flows (`shop/redact`, `customers/redact`, `customers/data_request` are exactly the mandatory topics this registry handles) — based on a `shop` value that an attacker fully controls while still passing HMAC validation. This satisfies the Critical "cross-tenant access" bar, since a malicious merchant can make the app process attacker-controlled webhook content under another merchant's shop identity.

### Likelihood Explanation
Requires only that the attacker be a legitimate (even trial) merchant who installs the target app — no privileged credentials, TLS interception, or leaked secrets are needed. They passively receive real signed webhook traffic for their own shop and can freely replay it with a modified `shop-domain` header. This is easily reachable through the gem's own public `Registry.process` / `Webhooks::Request` API.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values to the signed payload rather than trusting unsigned headers. Concretely: include shop domain in the signable string used for HMAC computation, or require the host application to independently verify that `request.shop` corresponds to a shop that has a currently valid, stored access token/webhook registration before invoking the handler — and document this requirement clearly, since currently `Registry.process` performs no such check.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers an event (e.g., `orders/create`), receiving a genuinely HMAC-signed webhook POST from Shopify containing body `B` and header `X-Shopify-Hmac-Sha256: H` (computed with the app's shared `client_secret` over `B`), plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the exact same body `B` and `X-Shopify-Hmac-Sha256: H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged header successfully (only checks presence, not correctness) — [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H` — [7](#0-6) .
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and performs shop-scoped business logic believing the event genuinely originated from `victim.myshopify.com`.

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
