### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) identity fields are not covered by the HMAC signature, allowing shop-domain spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the shop identity (`shop-domain` header) that the gem hands to application webhook handlers is taken from an unauthenticated header. Because the signable string never binds the shop, topic, or webhook id to the signature, any request whose body byte-for-byte matches a body the attacker has legitimately received (with a valid HMAC for their own shop) can be replayed with a forged `shop-domain` header pointing at a different, victim tenant, and it will still pass `HmacValidator.validate`.

### Finding Description
`Registry.process` treats a webhook request as authentic solely based on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

The validator recomputes the HMAC and compares it to the signature supplied by the caller: [2](#0-1) 

But the signable string for a webhook request is defined as just the raw body — none of the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) participate in the signature: [3](#0-2) 

After validation succeeds, `Registry.process` passes the *unauthenticated* `request.shop` straight into the handler's metadata, which the host application uses to attribute the event to a tenant: [1](#0-0) 

The equality the code implicitly assumes but never enforces is:
`shop bound by HMAC == shop delivered to handler (request.shop)`

In reality: `shop bound by HMAC` is undefined (the HMAC binds only the body bytes), while `shop delivered to handler` is attacker-controllable header content. Any party that has legitimately received one authentic webhook for their own shop (e.g., by installing the same app on a shop they control) possesses a `(body, hmac)` pair that is valid forever for that exact body. They can resend that identical body to the victim application's webhook endpoint while substituting the `shop-domain` (and `topic`/`webhook-id`) header to claim it originated from a different, victim shop. `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` invokes the handler with attacker-chosen `shop`, letting the attacker inject events attributed to a tenant they do not control.

### Impact Explanation
This breaks the tenant/shop identity binding that host applications rely on when using `WebhookMetadata#shop` to decide which merchant's records to update, and constitutes cross-tenant data confusion/injection using only unprivileged access (a shop the attacker legitimately controls) — no `client_secret`, access token, or privileged account is required to forge the identity field, only knowledge of the `client_secret` is needed to keep computing valid HMACs for one's own tenant's genuine traffic, which every merchant that installs the app already has via Shopify-originated deliveries.

### Likelihood Explanation
Any developer/merchant who installs the app on their own store receives genuine, validly-signed webhook deliveries. Capturing and replaying one of those requests with a modified `shop-domain` header against the same app's public webhook endpoint is trivial and requires no special access.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signature (e.g., verify against a signature computed over `shop + topic + body`, or require host applications to cross-check `request.shop` against a set of shops with an active install/session before trusting `WebhookMetadata#shop`). At minimum, document in `Registry.process` that `request.shop` is not authenticated by the HMAC and must be independently verified by the caller.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a real webhook delivery, e.g.:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"id":1}
   ```
2. Attacker resends the exact same body and HMAC to the app's webhook endpoint but changes the shop header:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-hmac>
   x-shopify-shop-domain: victim.myshopify.com
   Body: {"id":1}
   ```
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `body` against the HMAC (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` even though no request from Shopify for `victim.myshopify.com` ever occurred, letting the attacker inject/attribute fabricated webhook events to the victim tenant.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
