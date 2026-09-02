### Title
Webhook shop-domain attribution is not covered by the HMAC signature, allowing cross-tenant spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (and `topic`/`webhook_id`) values used by `ShopifyAPI::Webhooks::Registry.process` to attribute the webhook to a tenant are read from HTTP headers that are never included in the signed material.

### Finding Description
`Registry.process` gates webhook handling on `Utils::HmacValidator.validate(request)`, then immediately hands the handler a `WebhookMetadata` built from `request.shop`, `request.topic`, and `request.parsed_body` [1](#0-0) . `HmacValidator.validate` computes the signature strictly from `verifiable_query.to_signable_string`, which for `Webhooks::Request` returns only `@raw_body` — none of the headers are part of the signable string [2](#0-1) [3](#0-2) . The `shop` accessor is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cross-check against the signed body [4](#0-3) [5](#0-4) .

This breaks the identity binding `shop signed by HMAC == shop delivered to the handler`. An unprivileged user who legitimately installs the app on their own shop (Shop A) can generate a body + valid HMAC signature for their own tenant (since Shopify sends them real webhooks, or because the HMAC only requires knowledge of the raw bytes, not any secret contribution tied to the shop). They can then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain (Shop B). `HmacValidator.validate` still succeeds because it only checks body integrity against the secret, never verifying which shop the body belongs to. `Registry.process` then invokes the handler with `shop: "shop-b.myshopify.com"` and attacker-controlled `body`, causing the app to process/store attacker data as if it originated from Shop B — a cross-tenant data-injection primitive.

### Impact Explanation
This crosses a tenant boundary: data attributed to one merchant (Shop B) is actually attacker-controlled content originating from a different, unprivileged actor (Shop A). Any host application that persists webhook payloads keyed by `WebhookMetadata#shop` (order/customer/GDPR data, inventory, etc.) can have its per-tenant data poisoned or its GDPR redact/data-request handling misdirected, without ever compromising `api_secret_key` or an access token. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires the attacker to be a merchant/developer who has legitimately installed the app (or otherwise obtained one valid `(raw_body, hmac)` pair from their own store's webhook traffic) and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers — both are unprivileged-internet-user actions. No secrets, tokens, or elevated access are needed, making this readily reachable.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the HMAC-verified material, or otherwise cryptographically tie the header-derived shop domain to the request the HMAC was computed over — e.g., include the shop domain in `to_signable_string`, or require the host application to cross-check the header shop against a shop already known to be associated with that specific delivery (via Shopify's webhook ID lookup) before trusting `WebhookMetadata#shop`. At minimum, document prominently that `request.shop`/`topic`/`webhook_id` headers are unauthenticated and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker owns/operates Shop A with the app installed and can trigger (or has previously captured) a legitimate webhook delivery, giving them a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's `api_secret_key`.
2. Attacker sends a POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (the victim) and `x-shopify-topic` to a topic of choice.
3. `ShopifyAPI::Webhooks::Request.new` parses the spoofed headers [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the body/HMAC pair is genuinely valid [7](#0-6) .
4. The registered handler receives `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: <attacker body>, ...)` [8](#0-7) , and the host application processes/stores attacker-controlled data under Shop B's tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```
