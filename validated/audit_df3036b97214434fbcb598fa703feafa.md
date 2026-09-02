This confirms the finding: the webhook `Request` class's HMAC signature only covers the raw body (`to_signable_string` returns `@raw_body`), while the `shop` (from `shopify-shop-domain` header), `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers and passed downstream to the handler as trusted tenant-identifying metadata.### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are trusted from unauthenticated HTTP headers while the HMAC only signs the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `api_version`, and `webhook_id` purely from HTTP headers, but `to_signable_string` — the value that the HMAC signature actually covers — is only the raw request body. [1](#0-0) 
`Registry.process` validates the HMAC against the body only, then forwards the unauthenticated `shop` header straight into the `WebhookMetadata` struct passed to the app's handler as the tenant identity. [2](#0-1) [3](#0-2) 

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, body ‖ shop ‖ topic ‖ webhook_id)`, i.e., the tenant-identifying metadata should be cryptographically bound to the signature that authenticates the request. Instead the actual binding implemented is `hmac == HMAC(secret, body)` only, per `to_signable_string` returning `@raw_body`. [4](#0-3) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, `shopify-webhook-id`) with no cryptographic tie to those values. [5](#0-4) 

`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string`, so for a `Request` object it validates the HMAC solely against `@raw_body`, never checking the headers at all. [6](#0-5) 

`Registry.process` then uses `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` — all header-derived and unverified — to build the `WebhookMetadata` that the host application's handler treats as trusted tenant identity for the incoming event. [2](#0-1) 

Since the app's `api_secret_key` is shared across all shops that install the app (it's the app's own client secret, not per-shop), any two webhook deliveries generated for the same app — regardless of which merchant triggered them — are HMAC-valid over identical bodies. An unprivileged attacker who can install/operate their own shop (or otherwise trigger/observe a legitimately signed webhook delivery to their own app instance) can capture a `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header rewritten to name a **different** merchant's shop. `Utils::HmacValidator.validate` will still succeed because it only checks the body against the shared secret, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop. [2](#0-1) 

### Impact Explanation
This breaks the tenant-isolation guarantee that host applications rely on this gem to provide: "if `HmacValidator.validate(request)` passes, `request.shop` can be trusted as the originating shop." Any consuming application that keys per-shop state, authorization, or data mutation off `WebhookMetadata#shop` (the field this gem hands it) can be made to process a spoofed shop identity for an otherwise-valid, gem-verified webhook. This is a cross-tenant identity-binding failure directly rooted in this gem's `Request`/`Registry`/`HmacValidator` code, matching the "Critical - cross-tenant access" category, since it lets one authenticated tenant (the attacker's own shop installation) forge webhook metadata attributed to another tenant while passing this gem's own signature check.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker must be able to obtain at least one genuinely HMAC-signed `(body, hmac)` pair, which requires operating (or having) their own shop with the app installed — an unprivileged-but-real prerequisite that does not require the app's `client_secret`, an access token, or any other privileged credential. Once obtained, forging the header value requires no cryptographic secret at all, since the header is entirely outside the signed data.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signable string used for HMAC verification in `lib/shopify_api/webhooks/request.rb#to_signable_string`, or otherwise have `Utils::HmacValidator`/`Registry.process` cross-check the header-derived `shop` against a value recoverable from the signed payload, so that the shop identity cannot be altered independently of the signature.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) for that shop; Shopify delivers a POST with body `B` and header `shopify-hmac-sha256: H` where `H = HMAC(secret, B)`.
2. Attacker replays this exact `(B, H)` pair to the app's webhook endpoint but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shopify-shop-domain" => "victim-shop.myshopify.com", "shopify-hmac-sha256" => H})` is constructed; `shop` returns `"victim-shop.myshopify.com"` [7](#0-6) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares to `H` — this succeeds because `to_signable_string` only returns `B` [8](#0-7) [4](#0-3) .
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` [9](#0-8) , causing the host app to process attacker-controlled data as if it originated from the victim shop.

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
