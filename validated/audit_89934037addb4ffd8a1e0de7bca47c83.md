Confirmed. This gives sufficient root-cause evidence.

### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook only by checking the HMAC over the raw request body via `Utils::HmacValidator.validate`. The `shop` value that is handed to the app's `WebhookHandler` is read directly from the `x-shopify-shop-domain` HTTP header and is never part of the signed material, so it is not bound to the HMAC that authenticates the request.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose `to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) is instead pulled straight out of the request headers: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (the raw body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` uses this validation result to authorize the whole request, then forwards the header-derived, unauthenticated `request.shop` to the app's handler as the authoritative tenant identity: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop header used by the handler == shop cryptographically bound to the HMAC`. Because the HMAC only signs the body, this equality does not hold — the `shop` field is a "field acted on but not covered by the HMAC." Since the `api_secret_key` for a public app is shared across all installing shops (it is not per-tenant), any unprivileged merchant who has installed the app can capture one legitimate, validly-signed webhook delivered to their own shop (e.g., `orders/create` with body `{...}`) and replay the identical `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still succeed because it only re-derives the signature from the (unchanged) body, and `Registry.process` will call the handler with `WebhookMetadata.new(shop: <attacker-chosen domain>, body: <replayed body>, ...)`.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for HTTP webhooks: an attacker who is nothing more than an installer of the app (no special privilege, no leaked secret, no access token) can make the app process a webhook body under a shop identity of their choosing. Any handler logic that uses `data.shop` to look up, write, or act on per-tenant records (the documented and expected usage pattern shown in `docs/usage/webhooks.md`) can be tricked into attributing/applying attacker-controlled webhook data to a victim shop, i.e., cross-tenant access/confusion.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple shops (the normal case for public apps): the attacker only needs to be able to install the app on their own shop to receive one real, validly-signed webhook, and then replay it with a modified `shop-domain` header — no cryptographic secret, access token, or privileged account is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material checked during verification, or explicitly document/require that `WebhookHandler` implementations must independently verify that the shop from `data.shop` is one that legitimately installed the app and matches an already-authenticated session/record, never trusting the header value alone. Longer-term, include the shop domain as part of `to_signable_string` (if the underlying HMAC scheme changes to support this) or reject/flag any mismatch between the topic-registered handler context and the header-derived shop before invoking `handler.handle`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (no special privilege needed) and receives a legitimate webhook, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id":1,...}
   ```
2. Attacker replays the exact same body and `x-shopify-hmac-sha256` value, but changes only the shop header:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-hmac-for-body>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: {"id":1,...}
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (unchanged) `raw_body` against the (unchanged) HMAC — see [6](#0-5)  and [7](#0-6) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the request never originated from Shopify on behalf of that shop, demonstrating that the shop identity is unauthenticated relative to the HMAC.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
