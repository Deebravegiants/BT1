### Title
Webhook processing trusts `X-Shopify-Shop-Domain`/`Topic`/`Webhook-Id` headers that are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw body only, while the shop, topic, and webhook-id fields that `Registry.process` uses to route and attribute the webhook are read straight from unauthenticated HTTP headers.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` verifies the HMAC exclusively against that signable string [2](#0-1) . Meanwhile `Request#shop`, `#topic`, and `#webhook_id` are all pulled directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) with no cryptographic binding to the signed body [3](#0-2) .

`Registry.process` validates the HMAC and then unconditionally trusts `request.topic`, `request.shop`, and `request.webhook_id` to dispatch the handler and construct the metadata object passed to the app's business logic [4](#0-3) .

The binding that should hold is: `hmac_signed_bytes == bytes_that_determine_tenant_and_topic`. Here, `hmac_signed_bytes = raw_body` while `bytes_that_determine_tenant_and_topic = headers[shop-domain, topic, webhook-id]` — these are disjoint. A valid signature over a given `raw_body` says nothing about which shop or topic the request claims to be for.

### Impact Explanation
Since only the body is signed, an attacker who can obtain one genuine, validly-signed webhook delivery for a topic/body they control (e.g., a webhook fired for their own installed/dev store, which any merchant with an app installed can trigger) can replay that exact `raw_body` + `hmac-sha256` header pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still succeeds because it only recomputes the HMAC over the untouched body, so `Registry.process` will execute the registered handler with `WebhookMetadata` (via `handler.handle`) attributing the event to the attacker-chosen `shop` [5](#0-4) . Any host application logic keyed off `data.shop` (e.g. updating that shop's stored settings, honoring `shop/redact`/`customers/redact` compliance topics, or crediting/mutating tenant-specific state) executes for a tenant the attacker does not control — a cross-tenant integrity/confidentiality break driven entirely by this gem's failure to bind the shop identity to the signed payload.

### Likelihood Explanation
Exploitation requires only that the attacker possess a legitimately signed webhook body for the app's `client_secret` (trivially obtainable by installing the app on any store they control and capturing one delivered webhook) and the ability to POST to the app's public webhook endpoint with modified headers — no privileged credentials, TLS interception, or leaked secrets are required. This satisfies the scope's "unprivileged internet user" bar.

### Recommendation
Include the tenant/topic-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before use, e.g. by having `to_signable_string` incorporate a canonical representation of these headers rather than the raw body alone. At minimum, `Registry.process` should not trust `request.shop`/`request.topic` for tenant attribution unless they are provably bound to the verified signature.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers/receives a legitimate webhook for topic `orders/create`, capturing the exact `raw_body` and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker replays this exact `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Request.new` parses headers/body [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)` which recomputes the HMAC over `raw_body` only and succeeds (the body wasn't altered) [7](#0-6) .
4. The registered handler is invoked with `WebhookMetadata` carrying `shop: "victim.myshopify.com"` even though the request never originated from Shopify for that shop, causing the app to act on victim tenant data using attacker-supplied content.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
