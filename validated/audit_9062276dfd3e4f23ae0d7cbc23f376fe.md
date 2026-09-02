### Title
Webhook Shop/Topic Identity Not Bound to HMAC-Verified Payload Enables Cross-Tenant Webhook Spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then forwards the header-derived `shop` value to the application's handler as the trusted tenant identity, breaking the binding `HMAC-verified bytes == identity attributed to the request`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from headers that are never part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC of the body via `HmacValidator.validate`, then immediately trusts `request.shop` and `request.topic` (both taken from headers) to route and label the event delivered to the app's handler: [3](#0-2) 

`HmacValidator.validate` in turn only recomputes and compares the HMAC over `to_signable_string` (i.e. the raw body), never incorporating `shop`, `topic`, or any other header: [4](#0-3) 

The equality that should hold is:
`HMAC(secret, bytes-verified) == HMAC(secret, bytes-attributed-to-shop)`

but in this implementation:
`bytes-verified = raw_body` while `bytes-attributed-to-shop = shop-domain header (unauthenticated)`

Because a single app-level `api_secret_key` is shared across every merchant/tenant installation of a multi-tenant Shopify app, any merchant who is a legitimate (but potentially malicious) installer of the app receives genuinely Shopify-signed webhook deliveries for their own shop. That merchant can capture one such delivery (valid body + valid `X-Shopify-Hmac-Sha256`) and resend it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header rewritten to name a different, victim shop. `HmacValidator.validate` still succeeds because it only checks the untouched body against the secret, and `Registry.process` hands the handler a `WebhookMetadata` object whose `shop` field is the attacker-controlled header value, indistinguishable from a legitimate webhook for that victim shop.

### Impact Explanation
Any app built on this library that uses `WebhookMetadata#shop` (as delivered by `Registry.process`) to select which tenant's session/data record to update, delete, or query will act on the wrong shop when replayed as described. This is a cross-tenant confusion primitive: a webhook payload cryptographically proven to originate from Shopify for shop A can be attributed to shop B purely by an attacker rewriting an unauthenticated header, without possessing `api_secret_key`, an access token, or any Shopify credential belonging to shop B. This matches the Critical "cross-tenant access" impact bucket, since the shop identity binding that downstream handler code relies on is not actually enforced by the gem.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and possession of one genuine webhook delivery for any shop that installed the app (trivially obtainable by any merchant who installs a public app and lets Shopify deliver a webhook to them, or by any party who can observe/capture one such delivery in transit to the app). No secrets, tokens, or privileged access are required, matching the "unprivileged internet user" threat model.

### Recommendation
Bind the tenant/topic identity into the HMAC-verified content, or otherwise cryptographically tie headers to the body before trusting them:
- Include `shop`, `topic`, `api_version`, and `webhook_id` in the HMAC computation (as Shopify's server-side signing would need to support), or
- Independently verify the claimed `shop` against a value obtained through an authenticated channel (e.g., cross-check against the shop that owns the currently active session/webhook registration, keyed by `webhook_id` looked up via the Admin API) before acting on `WebhookMetadata#shop`, rather than trusting the raw header value implicitly once the body HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g., `orders/create`), capturing the raw body `B` and the header `X-Shopify-Hmac-Sha256: H` (a valid HMAC of `B` under the app's shared `api_secret_key`).
2. Attacker resends an HTTP POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since body is untouched)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (rewritten)
   - Header `X-Shopify-Topic:` unchanged or rewritten as desired
3. `ShopifyAPI::Webhooks::Request.new` parses these headers into `shop = "victim-shop.myshopify.com"`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `B` — see `lib/shopify_api/webhooks/request.rb` `to_signable_string` (raw body) and `lib/shopify_api/utils/hmac_validator.rb` `validate_signature`.
5. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...)` — see `lib/shopify_api/webhooks/registry.rb` lines 198-199 — causing the app to process order/customer/data-mutating webhook content while believing it belongs to `victim-shop.myshopify.com`.

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
