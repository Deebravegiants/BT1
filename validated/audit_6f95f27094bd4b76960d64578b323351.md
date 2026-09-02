This confirms the analog. The `x-shopify-shop-domain` header (`request.shop`) is passed to the webhook handler as the authoritative tenant identity, but it is excluded from the HMAC-signed content — `Request#to_signable_string` returns only `@raw_body`.This confirms the root cause precisely: `HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, which for `Request` returns `@raw_body` exclusively — the `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers are entirely excluded from the signed content, yet `Registry.process` trusts `request.shop` as the tenant identity passed to the app's handler.

### Title
Webhook `shop` (and topic/webhook_id/api_version) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` verifies the HMAC solely against that signable string using the app-wide `Context.api_secret_key` [3](#0-2) . `Webhooks::Registry.process` then treats `request.shop` as trustworthy tenant identity and forwards it, unbound to the HMAC, straight to the app's handler as `WebhookMetadata#shop` [4](#0-3) , and `WebhookMetadata` declares `shop` as a plain trusted `String` field [5](#0-4) .

### Finding Description
The identity binding that should hold is:
`shop_header_used_by_handler == shop_that_the_HMAC_actually_authenticates`

Because `to_signable_string` only returns `@raw_body`, this equality does not hold — the HMAC authenticates *only the body bytes*, never the `shop-domain` header. Since a single app-level `api_secret_key` is used to sign webhooks for every shop that installs the app (not a per-shop secret), any user who can install the app on their own shop — an ordinary unprivileged internet user — automatically becomes an oracle for valid `(body, hmac)` pairs signed with the app's shared secret.

An attacker who installs the app on their own shop, triggers a webhook event, and captures the resulting `(raw_body, x-shopify-hmac-sha256)` pair can replay that exact body and signature to the app's webhook endpoint while swapping the `x-shopify-shop-domain` header to a victim shop's domain. `HmacValidator.validate` will pass because it never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-chosen) body originated from the victim shop.

### Impact Explanation
This crosses a tenant boundary using only a credential (the shared `api_secret_key`) indirectly proven valid via the attacker's own installation — no access token or victim secret is required. Any host application that keys business logic off `WebhookMetadata#shop` (e.g., "update order/product/customer state for shop X", audit logging, billing, or triggering per-shop side effects) can be made to apply attacker-controlled webhook bodies to a victim shop's context, i.e. cross-tenant data confusion/injection. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app builder who installs the library as documented and simply trusts `data.shop` from `WebhookMetadata` (as shown in the library's own webhook docs) — this is the intended, documented usage pattern [6](#0-5) . No special privileges beyond installing the app on any shop (something any merchant/developer can do) are needed to obtain a valid `(body, hmac)` pair to replay against a different shop header.

### Recommendation
Include the shop domain (and ideally the other Shopify-supplied identity headers, or use the webhook's `X-Shopify-Api-Version`/topic if they must remain flexible) in the HMAC-signed content, or independently verify that `shop-domain` is cryptographically tied to the request (e.g., derive/validate it from a signed component) before constructing `WebhookMetadata`. At minimum, `to_signable_string` should incorporate the `shop`, `topic`, and `webhook_id` headers alongside the raw body so `HmacValidator.validate` binds them to the signature.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they control) and triggers a subscribed webhook (e.g., `orders/create`) with attacker-controlled order content.
2. Shopify sends the app `POST /callback/orders/create` with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, and the attacker-controlled JSON body.
3. Attacker captures `raw_body` and the valid `x-shopify-hmac-sha256` value.
4. Attacker replays the identical request to the same endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only [7](#0-6)  — it matches, since the header was never part of the signed content.
6. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)` [8](#0-7)  and invokes the app's handler, which now believes the attacker's payload legitimately originated from the victim shop.

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
