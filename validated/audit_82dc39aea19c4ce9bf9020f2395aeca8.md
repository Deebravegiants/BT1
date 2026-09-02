### Title
Webhook shop-domain header is trusted for tenant attribution but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` and `topic` values used to route and attribute an incoming webhook entirely from unauthenticated HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`), while the HMAC signature that `Registry.process` validates covers only the raw request body. This breaks the intended binding "bytes verified == bytes trusted for shop attribution."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from HTTP headers, which are never included in the signed payload: [2](#0-1) 

The dispatcher, `Registry.process`, validates the request purely by checking the HMAC over the body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.topic` and `request.shop` to route to a handler and build the `WebhookMetadata` passed to app code: [3](#0-2) 

`HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string` (the raw body for webhooks) and compares it against the `hmac-sha256` header — it never incorporates `shop-domain`: [4](#0-3) 

**Binding that should hold:** `shop-domain header == shop that authored/signed the body`. Because the app's `client_secret` (api_secret_key) is the same for every shop that installs the app, any merchant that installs the app can trigger a legitimate webhook for their own shop and obtain a body + valid HMAC pair signed with the app's shared secret. That merchant can then replay/craft an HTTP request to the app's webhook endpoint using the same (valid) `hmac-sha256` and raw body but substitute the `x-shopify-shop-domain` header with an arbitrary victim shop domain. `HmacValidator.validate` still passes because it never checks the header, and `Registry.process` builds `WebhookMetadata` with the forged `shop`, handing the app's `WebhookHandler#handle` code data that is falsely attributed to the victim tenant.

### Impact Explanation
This is a cross-tenant confusion vector: the shop identity trusted by the app's webhook-handling code (used for session/data lookups, audits, per-tenant business logic) is not bound to the cryptographically verified bytes. An attacker who is a legitimate (if malicious) merchant of the same app can make the app process/store data as if it originated from a different shop, potentially corrupting per-tenant records, triggering privileged actions bound to the victim shop's session, or bypassing app-side checks tied to the shop parameter. This matches the "cross-tenant access" Critical impact category since the tenant boundary enforced by shop attribution can be crossed by any app-installing merchant with no special privileges over the victim shop.

### Likelihood Explanation
Likelihood is moderate-to-high in intent but requires that the app's handler logic actually trusts `WebhookMetadata#shop` for tenant-sensitive decisions (a very common pattern, e.g. `ShopifyApp`-style webhook consumers that look up/update the shop's record by `data.shop`). Any account that has installed the app (an "unprivileged internet user" relative to other tenants) can generate a signed body for itself and swap the header, since HTTP headers are fully attacker-controlled outside of TLS-terminated infrastructure and the gem performs no header authentication.

### Recommendation
Bind the `shop` (and ideally `topic`) header value into the signed material, or otherwise cryptographically/contextually verify that the `shop-domain` header matches the tenant that owns the signed payload before constructing `WebhookMetadata`. At minimum, downstream consumers must be warned/forced to independently validate `shop-domain` against a known/expected shop for the specific delivery (e.g., compare against the webhook subscription's registered shop) rather than trusting the header as authenticated. Update `Request#to_signable_string` or add a secondary check within `Registry.process` that rejects requests when the shop header cannot be corroborated.

### Proof of Concept
1. Attacker (`shop-a.myshopify.com`) installs the target app and triggers any subscribed webhook topic (e.g. `orders/create`) for their own shop, capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent — both valid because they were signed with the app's shared `client_secret`.
2. Attacker crafts an HTTP request to the app's webhook endpoint reusing that exact raw body and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: shop-victim.myshopify.com` and desired `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`@raw_body` only) — this matches, so validation passes: [5](#0-4) 
4. `request.shop` returns the attacker-supplied `shop-victim.myshopify.com` header value: [6](#0-5) 
5. `WebhookMetadata.new(topic: ..., shop: request.shop, body: request.parsed_body, ...)` is handed to the app's `WebhookHandler#handle`, which will process attacker-controlled body content under the victim's shop identity: [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
