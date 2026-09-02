### Title
Webhook HMAC Only Covers the Raw Body, Not the `shop`/`topic` Headers — Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, and `webhook_id` are read from unsigned HTTP headers. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` for tenant attribution after validating only the body's HMAC, so a valid `(body, hmac)` pair from one shop can be replayed with a forged `shop-domain` header pointing at a victim shop.

### Finding Description
`HmacValidator.validate` computes the signature purely from `to_signable_string`: [1](#0-0) 
which is defined as just the raw body: [2](#0-1) 
`shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers and are never part of the signed material: [3](#0-2) 

`Registry.process` validates only this body-bound HMAC, then hands `request.shop` (from the unsigned header) directly to the app's handler as the tenant identifier: [4](#0-3) 

The identity binding that should hold is: `shop header == shop bound by hmac`. In reality, the HMAC only proves `raw_body == hmac(raw_body, secret)`; it says nothing about which shop the body belongs to. An unprivileged user can install the app on a store they control, capture one legitimately-signed `(raw_body, hmac)` pair from their own webhook delivery, and replay that exact body/hmac pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header for a victim shop. `HmacValidator.validate` still returns `true` (body and hmac are unchanged and correctly signed), and `Registry.process` dispatches the handler with `shop: request.shop` set to the victim's domain.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` to select/attribute the tenant record it updates (e.g., look up the session/store for that shop and persist order/product/customer data) can be made to attribute attacker-controlled webhook payloads to an arbitrary victim shop, since the shop-to-signature binding does not exist. This constitutes cross-tenant data injection — the strongest applicable impact category (cross-tenant access) — reachable without the app's `client_secret`, access token, or any privileged credential; the attacker only needs their own free/dev shop to legitimately obtain a signed body once.

### Likelihood Explanation
High for any consumer of this gem that keys per-shop state off `WebhookMetadata#shop` without independently re-validating the shop against something else (most integrations do exactly this, since the gem's own documentation and API surface present `request.shop`/`data.shop` as trustworthy once `HmacValidator.validate` passes). Getting one legitimately signed webhook only requires installing the app as an ordinary merchant.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them to the HMAC) so that the signature attests to the full context, not just the body bytes. At minimum, document prominently that `request.shop`/`webhook_id`/`topic` are unauthenticated and must not be trusted for tenant attribution without an independent check against a known-good session.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they legitimately control) and triggers any webhook (e.g., `orders/create`), capturing the raw request body `B` and its valid `X-Shopify-Hmac-Sha256` header `H`.
2. Attacker sends a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and `X-Shopify-Topic` set to the same original topic.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers as-is: [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `B` and matches `H` — validation succeeds despite the shop header being forged: [6](#0-5) 
5. The registered handler is invoked with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-supplied data as if it belonged to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
