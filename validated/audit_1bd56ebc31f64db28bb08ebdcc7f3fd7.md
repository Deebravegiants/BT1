### Title
Webhook `shop`, `topic`, and `webhook-id` fields are trusted from unauthenticated headers but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken directly from HTTP headers to build `WebhookMetadata` that is handed to the app's `WebhookHandler`. None of those header-derived fields are included in the signed data.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 
`to_signable_string` returns only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from HTTP headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates only this HMAC-over-body, then immediately trusts `request.shop` and `request.topic` to build the metadata dispatched to the app's handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain, unauthenticated `String` field passed straight to the host application's handler: [4](#0-3) 

The identity binding that is broken: **the tenant (`shop`) that the library asserts is authenticated == the tenant whose bytes were actually HMAC-verified**. In fact only the *body* is HMAC-verified; the `shop` (and `topic`/`webhook_id`) are unauthenticated header values with no relationship to the signed content. Critically, for a given app, the webhook HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is identical across every merchant installation — it is not shop-specific. This is confirmed by the shared `Utils::HmacValidator.validate` logic used identically for both OAuth callbacks and webhooks: [5](#0-4) 

Consequently, any entity capable of installing the public app on their own store (an "unprivileged internet user" from the app's perspective) receives genuine, correctly-HMAC-signed webhook deliveries for their own shop. Because the signature covers only the JSON body and never the `shop-domain` header, that same body+HMAC pair remains valid when replayed with an arbitrary, attacker-chosen `shop-domain` header value. The library will report this replayed delivery as verified and hand `WebhookMetadata` with a spoofed `shop` to the host application's handler, which typically uses `data.shop` to route the payload to the correct merchant's data/session store.

### Impact Explanation
This breaks the tenant isolation the library is expected to guarantee via `Registry.process`/`Utils::HmacValidator.validate`: an attacker who legitimately installs the app on Shop A can forge webhook events (e.g. `orders/create`, `customers/update`, GDPR topics) that the host app will process as if they came from Shop B, since the only authenticity check performed by the gem (`HmacValidator.validate`) never binds `shop` to the signed bytes. This is cross-tenant data injection/spoofing attributable to the gem's own webhook verification logic, not to host application misuse, since the gem does not expose any way to verify the shop identity as part of signature validation.

### Likelihood Explanation
Requires only: (1) ability to install the target public app on an attacker-controlled shop (normal, unprivileged action for any public Shopify app), (2) capturing one legitimate webhook (body + `X-Shopify-Hmac-Sha256`) delivered to that attacker-controlled shop, and (3) replaying it to the same webhook endpoint with a different `X-Shopify-Shop-Domain` header. No access to the app's `client_secret`, access tokens, or any victim-shop credentials is needed.

### Recommendation
Bind the tenant-identifying and routing headers (`shop`, `topic`, `webhook_id`, `api_version`) into the signed data used by `HmacValidator`, or otherwise cryptographically tie the accepted `shop` to the specific delivery (e.g., cross-check against Shopify's registered subscription for that topic/shop, or require the host app to validate `shop` against its own known-installed-shops list before trusting `WebhookMetadata`). At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a tenant boundary without additional verification.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`.
2. Capture a real webhook delivery: raw body `B`, header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's shared `client_secret`), `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Resend the same request to the app's webhook endpoint, keeping body `B` and `X-Shopify-Hmac-Sha256: H` unchanged, but setting `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` returns only `B`: [3](#0-2) 
5. The host app's `WebhookHandler#handle` receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, processing attacker-controlled data as if it originated from `victim.myshopify.com`.

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
