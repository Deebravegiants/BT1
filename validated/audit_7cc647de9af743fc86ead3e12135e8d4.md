### Title
Webhook shop identity spoofing via `shop-domain` header not covered by HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) for an incoming webhook from the `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. This breaks the identity binding `hmac-verified-bytes == tenant-identifying-bytes`: the bytes that are cryptographically authenticated (the body) are not the same bytes used to determine which shop the webhook belongs to (the header).

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#hmac` and `#shop` are both read from HTTP headers, independently of the body: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` (i.e., only the raw body) and compares it against `request.hmac`. After that check passes, `request.shop` (from the unauthenticated `shop-domain` header) is trusted and passed straight into `WebhookMetadata`, which handlers use to key their tenant-scoped logic: [3](#0-2) 

`Utils::HmacValidator.validate` confirms the signature check is only over `to_signable_string`, i.e. the body, and never incorporates the shop header: [4](#0-3) 

Because the `shop-domain` header is outside the HMAC's protected scope, any party who can obtain one genuinely-signed webhook body+HMAC pair for their own shop (i.e., any merchant who installs the public app, an ordinary unprivileged flow requiring no leaked secret) can replay that exact body and HMAC to the app's webhook endpoint while substituting a different value in the `X-Shopify-Shop-Domain` header. The signature will still validate (it only checks the body bytes), but `Registry.process` will hand the handler a `WebhookMetadata` claiming the body belongs to an arbitrary victim shop of the attacker's choosing. If the host application uses `WebhookMetadata#shop` to select or scope which tenant's records to update (the intended and documented use of this field), the attacker can inject data/webhook events attributed to a shop they do not own — a cross-tenant identity confusion entirely mediated by this gem's `Request`/`Registry` design, not by any misuse on the host app's part (the host app is only following the gem's documented contract of trusting `WebhookMetadata#shop` after `Registry.process` succeeds).

### Impact Explanation
This qualifies as cross-tenant access: an attacker-controlled webhook payload can be attributed to an arbitrary shop identifier after passing this gem's own signature check, letting the attacker inject or forge events for a tenant they don't control, purely by exploiting the gap between what is signed (body) and what is trusted for tenant identity (header).

### Likelihood Explanation
Medium-High. The prerequisite — possessing one valid signed webhook (body + `X-Shopify-Hmac-Sha256`) — is trivially obtainable by any unprivileged party who installs the app on their own shop (assuming the app allows any shop to install, which is the common case for public Shopify apps) and simply captures one of the delivered webhook requests. No secret key, privileged account, or leaked credential is required; only re-sending an HTTP request with one header value changed.

### Recommendation
Bind the shop identity to the HMAC-verified content: include the `shop-domain` (and ideally `topic`, `webhook-id`) header values as part of the signed payload used for HMAC verification (`to_signable_string`), or independently verify that the shop in the header matches the shop that the app expects/has on record for that specific webhook subscription before trusting `WebhookMetadata#shop` in handler dispatch.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256: H` header Shopify sent — `H` is a valid HMAC(`B`, client_secret).
2. Attacker replays the request to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `B` and matches `H` — validation succeeds ( [5](#0-4) ).
4. `request.shop` returns `"victim-shop.myshopify.com"` from the spoofed header ( [6](#0-5) ), and this value is forwarded to the handler via `WebhookMetadata.new(... shop: request.shop ...)` ( [7](#0-6) ), causing the attacker's body to be processed as if it originated from the victim shop.

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
