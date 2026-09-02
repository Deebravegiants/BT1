### Title
Webhook HMAC verifies only the request body, allowing shop-domain header spoofing for cross-tenant webhook injection - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature validated by `Utils::HmacValidator.validate` proves nothing about the `shop-domain`, `topic`, `webhook_id`, or `api_version` headers. `Registry.process` nevertheless takes `request.shop` straight from that unsigned header and uses it as the tenant identity forwarded to the host app's webhook handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. `HmacValidator.validate_signature` computes the signature over exactly that string: [2](#0-1) 
So a valid HMAC only certifies "this body was signed with the app's `client_secret`" — it says nothing about which shop the body belongs to. `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no binding to the signature: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the app's handler: [4](#0-3) 

The identity binding broken here is: **shop implied by a validly-HMAC'd body ≠ shop stored in `WebhookMetadata.shop` used by the host app as the tenant key.** The gem's own documentation instructs host apps to trust `data.shop` directly for tenant-scoped work (e.g. enqueuing per-shop jobs): [5](#0-4) [6](#0-5) 

Because the app's `client_secret` is shared across every shop that installs the app (it is not shop-specific), any merchant who installs the app on their own store can trigger a legitimately-signed webhook body for their own store's data (e.g. `orders/create` with attacker-controlled order content, or `customers/data_request`). They can capture that raw body + valid HMAC, then POST it directly to the app's public webhook endpoint (a plain HTTP endpoint the host app exposes, per the documented controller pattern) with the `shop-domain` header swapped to a different, victim shop's domain. Because only the body is signed, `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` builds a `WebhookMetadata` claiming the victim shop as the source: [7](#0-6) 

### Impact Explanation
This is a cross-tenant confusion: an unprivileged attacker who is merely a merchant of one shop that installed the app (no special privilege, no leaked credentials) can make the app process attacker-controlled webhook data under an arbitrary victim shop's identity. Since host apps built against this gem are explicitly directed to key their per-tenant persistence/business logic off `data.shop`, this can lead to cross-tenant data injection/corruption for any multi-tenant app relying on this library's stated contract that a processed webhook's `shop` field is trustworthy.

### Likelihood Explanation
Likelihood is moderate-to-high: the attacker only needs (a) to install the app on their own store to obtain a validly-signed body/HMAC pair, and (b) to know or guess the app's public webhook path (typically fixed and often documented, e.g. `/webhooks` or `/callback/<topic>`). No access token, `client_secret`, or privileged account is required — the `api_secret_key` itself is never disclosed to the attacker, only its byte output on their own store's payload is captured and replayed with mismatched headers.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the signed material verified against the HMAC (mirroring how `AuthQuery#to_signable_string` includes `shop` per [8](#0-7) ), or otherwise cross-validate that the shop-domain header corresponds to a shop actually subscribed to the webhook/topic before constructing `WebhookMetadata`, rejecting mismatches with `Errors::InvalidWebhookError`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker triggers an `orders/create` event on their own store, capturing the raw JSON body and the `X-Shopify-Hmac-Sha256` header Shopify sends — this HMAC is valid because it was computed with the app's real `client_secret`.
3. Attacker POSTs directly to the app's public webhook endpoint (e.g. `POST /callback/orders/create`) with:
   - Body: the captured raw body (unmodified, so the HMAC still matches).
   - Header `X-Shopify-Hmac-Sha256`: the captured valid HMAC.
   - Header `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (swapped).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only the (unmodified) body is checked: `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host app processes attacker-controlled order data as if it belongs to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L19-29)
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

**File:** BREAKING_CHANGES_FOR_V15.md (L113-124)
```markdown
### New implementation
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
    end
  end
end
```
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
