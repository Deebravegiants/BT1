## Title
Webhook shop/topic identity spoofing — HMAC covers only the raw body, not the `shop-domain`/`topic` headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` but defines `to_signable_string` to return only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only proves that the body was signed with the app's `client_secret`; it never binds that signature to the `shop-domain` header that `Registry.process` subsequently trusts and hands to the app's webhook handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (i.e. the body only) and compares it to the `hmac` header: [3](#0-2) [4](#0-3) 

After that check passes, `process` forwards `request.shop` unmodified to the app's handler as authenticated tenant context: [5](#0-4) 

Because Shopify webhook HMACs are computed with the app's single `client_secret` (shared across every shop that installs the app, not a per-shop secret), a malicious merchant who has installed the app can:
1. Receive a legitimate webhook for their own shop, obtaining a valid `(body, hmac)` pair signed by the app's client secret.
2. Craft an HTTP POST to the app's webhook endpoint with that exact same `body`/`hmac`, but with a **forged `x-shopify-shop-domain` header** naming a victim shop, and optionally a forged `x-shopify-topic` header.
3. `Utils::HmacValidator.validate` accepts it, because the signature only ever covered the body, and the forged `shop`/`topic` headers are not part of the equality the HMAC is supposed to enforce.

The equality that should hold is: **HMAC-verified bytes == bytes the handler treats as tenant identity (`shop`)**. In this implementation, `HMAC-verified bytes (body only) != bytes used for tenant identity (shop-domain header)`, breaking that binding.

### Impact Explanation
This is a cross-tenant identity-binding failure: the field the application logic relies on to select /namespace data for a merchant (`data.shop`, delivered via `WebhookMetadata`) is not covered by the HMAC that is supposed to authenticate the whole webhook payload. Any app that keys persistence, authorization, or side effects off `WebhookMetadata#shop` (the documented/intended usage per `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))`) can be made to process attacker-supplied body content under another (victim) shop's identity, since only the body content — not the shop attribution — is proven authentic.

### Likelihood Explanation
Requires an attacker to be a legitimate (even trial) merchant who has installed the target app, so they can observe at least one real, validly-signed webhook body/HMAC pair for their own shop (all shops share the same app `client_secret`, so the exact same signature validates for any shop header). No access to `client_secret`, tokens, or TLS interception is needed — only the ability to observe one's own webhook traffic and replay/relay an HTTP POST to the app's public webhook endpoint with modified headers.

### Recommendation
Include the tenant-identifying and topic fields (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signed payload used for verification, or otherwise cryptographically bind them to the body (e.g., verify against Shopify's registered webhook subscription for that specific shop, or require mutual TLS/webhook source IP allow-listing in addition to HMAC). At minimum, document clearly that `request.shop`/`request.topic` are unauthenticated header values and must not be trusted for tenant-scoping decisions without additional verification (e.g., cross-checking against an existing installed-shop record before honoring the header).

### Proof of Concept
1. Install the app on Shop A (attacker-controlled). Capture a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC-SHA256(client_secret, B)`).
2. Send a POST to the app's webhook endpoint reusing body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: shop-b.myshopify.com` (victim) instead of Shop A's domain.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`: [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` and attacker-chosen `body`, even though shop B never sent this webhook.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
