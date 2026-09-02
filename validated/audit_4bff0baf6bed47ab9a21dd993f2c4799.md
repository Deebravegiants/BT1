### Title
Webhook `shop` identity is read from an unauthenticated header while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook request's authenticity by HMAC-verifying only the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` fields taken directly from unauthenticated HTTP headers and hands them to the host application's handler as the tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only `@raw_body`: [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all pulled straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) .

`Registry.process` validates HMAC via `Utils::HmacValidator.validate(request)` and, once that passes, forwards `request.shop` (the header value) straight into `WebhookMetadata` which the host app's handler treats as the identity of the shop that sent the event: [3](#0-2) . `HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e., the raw body only) and compares it against the `hmac` header using `Context.api_secret_key`, which is the single app-wide secret shared across every shop that installs the app: [4](#0-3) . `WebhookMetadata.shop` is a plain `String` field with no further validation before being passed to the handler: [5](#0-4) .

This breaks the intended identity binding `shop (header, unauthenticated) == shop (identity acted on by host app)`. Since `api_secret_key` is one value per app, not per shop, any user who installs the app on their own store can obtain a genuinely-signed `(raw_body, hmac)` pair for their own shop, then replay that same body/HMAC pair to the app's webhook endpoint while substituting a different value in the `x-shopify-shop-domain` / `shopify-shop-domain` header. Because the header is never part of the signed material, `HmacValidator.validate` still passes, and the forged `shop` value is delivered to the host application's `WebhookHandler#handle` as if it were authentic.

### Impact Explanation
The gem's own documentation instructs host apps to trust `data.shop` directly, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`: [6](#0-5) . Any host application following this documented pattern to key off `data.shop` (e.g., to load that shop's session/access token, update per-shop state, or attribute the webhook body to a tenant) is exposed to cross-tenant data injection: an attacker-controlled shop can make the app process a webhook body under a victim shop's identity, or vice versa. This is a cross-tenant identity-binding break reachable by any unprivileged user who can install the app (a standard, unprivileged action for public apps), qualifying as Critical (cross-tenant access) per the rules.

### Likelihood Explanation
High likelihood: exploitation requires only (1) installing the target app on an attacker-owned shop to obtain a validly-signed webhook body/HMAC pair for a topic of choice, and (2) POSTing that same body/HMAC to the app's webhook callback URL with a forged `shop-domain` header value. No access token, `client_secret`, or privileged account is required — only participation as a normal merchant/user of the app, which satisfies the "unprivileged internet user" threat model.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the authenticated request by either including these header values in the signable string that the HMAC covers, or by cross-checking `request.shop` against an independently-verified source (e.g., the shop associated with the registered webhook subscription/session) before trusting it in `WebhookMetadata`. At minimum, document prominently that `data.shop` in `WebhookMetadata` is NOT authenticated by the HMAC and must not be used as a tenant-identity key without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, completing OAuth normally (unprivileged action).
2. Shopify sends a legitimate webhook to the app's callback URL with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` and replays it to the same endpoint, changing only the header:
   `x-shopify-shop-domain: victim-shop.myshopify.com`, keeping body `B` and `x-shopify-hmac-sha256: H` unchanged.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H...})` is constructed; `Utils::HmacValidator.validate` recomputes HMAC over `B` only, which still matches `H`, so validation succeeds: [7](#0-6) .
5. `Registry.process` calls the host handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`: [8](#0-7) , causing the host app to act on attacker-controlled body content under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
