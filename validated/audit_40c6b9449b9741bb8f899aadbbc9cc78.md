I have enough context to finalize the analysis. The `Utils::HmacValidator` only signs the raw request body for webhooks, while `Registry.process` trusts the unsigned `shop-domain`, `topic`, and `webhook-id` headers as the tenant/routing identity — this is the exact "field acted on but not covered by the HMAC" pattern.

### Title
Webhook tenant identity (`shop`, `topic`, `webhook_id`) is not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` from HTTP headers, but `to_signable_string` used for HMAC verification only covers `@raw_body`. `Registry.process` validates the HMAC and then trusts these unsigned header fields to route and attribute the webhook to a tenant, breaking the binding between "bytes verified" and "identity acted on."

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `hmac`, `topic`, `shop`, `api_version`, `webhook_id` are all read independently from headers [2](#0-1) . `HmacValidator.validate` computes the signature only over `to_signable_string` (i.e., the raw body) and compares it against the `hmac` header [3](#0-2) . `Registry.process` calls `Utils::HmacValidator.validate(request)` and, once it passes, immediately trusts `request.topic`, `request.shop`, and `request.webhook_id` — none of which were part of the signed bytes — to select the handler and construct `WebhookMetadata` that is handed to the app's business logic as the authoritative tenant/topic [4](#0-3) .

Because a single app-level `api_secret_key` is used to sign webhooks for every shop that has installed the app, any merchant who legitimately installs the app can capture a genuine `(raw_body, hmac)` pair delivered to their own shop. Since the `shop-domain`, `topic`, and `webhook-id` headers are not part of the signed content, that same `raw_body`/`hmac` pair remains valid when replayed with a different `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header pointing at a victim shop. `HmacValidator.validate` will still return `true` because it only re-derives the signature from `@raw_body`, and `Registry.process` will dispatch the forged request to the handler labeled with the attacker-chosen `shop`.

This breaks the identity equality that should hold: `bytes verified by HMAC == identity acted upon`. Here, `bytes verified (raw_body)` != `identity acted upon (shop, topic, webhook_id from headers)`.

### Impact Explanation
An attacker who is merely a legitimate, unprivileged merchant/user of the app on their own shop can forge webhook deliveries attributed to any other shop known to them (shop domains are not secret), injecting attacker-controlled body content into another tenant's webhook processing pipeline. Depending on the handler, this can lead to cross-tenant data corruption, spoofed events (e.g., fake `orders/create`, `app/uninstalled`, `shop/redact`), or state changes performed on behalf of a shop the attacker does not own — satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any app that exposes an HTTP webhook endpoint using this gem's `Webhooks::Registry.process`/`Request` as documented: the attacker only needs their own legitimate app installation to obtain one valid `(raw_body, hmac)` pair, then can replay it with a rewritten `shop-domain` header pointing at any other known shop. No access token, `client_secret`, or victim credentials are required.

### Recommendation
Bind the tenant/routing identity into the signed material, or otherwise cryptographically tie the `shop`, `topic`, and `webhook_id` headers to the request before trusting them:
- Include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (mirroring `AuthQuery#to_signable_string`'s approach of signing all security-relevant fields), or
- Have `Registry.process` cross-check `request.shop` against an expected/allow-listed shop for the current handler context, rather than trusting the header value unconditionally.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery, e.g. for topic `orders/create`, with headers `x-shopify-hmac-sha256: <valid_hmac>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, and body `raw_body`.
2. Attacker replays an HTTP POST to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. The app constructs `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` and calls `Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` computes `HMAC(api_secret_key, raw_body)` and compares to the (unchanged, still valid) `hmac` header — validation succeeds [5](#0-4) .
5. `Registry.process` dispatches `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker-controlled parsed body>, ...)` to the registered handler [6](#0-5) , which processes attacker-controlled data as if it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
