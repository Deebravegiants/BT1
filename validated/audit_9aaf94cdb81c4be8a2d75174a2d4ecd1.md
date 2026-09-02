### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `api_version`, and `webhook_id` as trusted, HMAC-verified data to the app's webhook handler, but its `to_signable_string` implementation only returns the raw body — none of these header-derived identity fields are actually part of the signed payload. `Utils::HmacValidator.validate` therefore authenticates the request body only, never the shop identity that gets forwarded to the handler.

### Finding Description
`Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from unauthenticated HTTP headers: [2](#0-1) 

`HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it to the `hmac` header — it never touches `shop`/`topic`/etc: [3](#0-2) 

`Registry.process` then forwards `request.shop` (an unauthenticated field) straight into `WebhookMetadata` and hands it to the app's handler as if it were verified: [4](#0-3) [5](#0-4) 

Because the app's `api_secret_key` is a single, app-wide secret (not per-shop), any shop that has installed the app can generate a request body/HMAC pair that is cryptographically valid for the app as a whole. The `shop` header is a purely cosmetic, unauthenticated label — it "acts on" the handler's business logic (as the tenant identifier) without being covered by the HMAC that is supposed to authenticate the whole request. This is precisely the identity-binding break described in the bug class: a field consumed by downstream logic (`shop`) is disjoint from the field actually checked by the authorization mechanism (`hmac` over `raw_body` only).

### Impact Explanation
An attacker who has installed the app on their own shop can trigger any event to obtain a legitimately-signed webhook body (HMAC computed with the app's real secret), then resend that same body to the app's webhook endpoint with the `x-shopify-shop-domain`/`shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still pass (it never inspects the shop header), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-controlled) payload originated from the victim shop. Any host application that uses `data.shop` from the gem's own `WebhookMetadata` as the tenant key (exactly as the gem's public API implies it should) will process attacker-supplied data under another merchant's identity — a cross-tenant confusion/cross-tenant access condition.

### Likelihood Explanation
Requires no privileged access, tokens, or `api_secret_key`/`client_secret` knowledge — only that the attacker install (or already have) the app on any shop, an action available to any unprivileged internet user. The only "skill" required is capturing one's own legitimately-signed webhook and re-sending it with an altered header, which is straightforward HTTP manipulation.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the signed payload verification, e.g., by having `to_signable_string` incorporate the shop-domain header (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop`/`host` in its signable string, at `lib/shopify_api/auth/oauth/auth_query.rb:33-43`), or by requiring callers to cross-check `WebhookMetadata.shop` against a shop that the app has an existing, authenticated session/install record for before trusting it as a tenant identifier.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`).
2. Shopify sends the app: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC(app_secret, body)>`, body `B`.
3. Attacker resends the identical body `B` and HMAC header to the app's webhook endpoint, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13`) validates successfully because it only checks `B` against the HMAC, ignoring the shop header.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, even though `victim-shop` never sent this webhook.

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
