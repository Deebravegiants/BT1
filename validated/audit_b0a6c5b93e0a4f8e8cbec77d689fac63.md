### Title
Webhook HMAC verification only covers the request body, not the `shop-domain`/`topic` headers, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `to_signable_string` by returning only the raw HTTP body, while the `shop` (from `X-Shopify-Shop-Domain`) and `topic` (from `X-Shopify-Topic`) values used to route and attribute the webhook are read directly from unauthenticated headers and never included in the signed material. [1](#0-0) [2](#0-1) 

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the expected signature purely from `verifiable_query.to_signable_string`, which for webhooks is `@raw_body`: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` accepts a request once `Utils::HmacValidator.validate(request)` passes, and then dispatches to the topic handler using `request.topic` and passes `request.shop` straight into `WebhookMetadata`, which the host app's `WebhookHandler#handle` treats as the authenticated tenant identity for the event: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop asserted in the HMAC-signed payload == shop attributed to the event by the gem`. Because the HMAC only signs the raw body bytes, and the same `Context.api_secret_key` is shared across every shop that installs the app, a valid `(body, hmac)` pair obtained from one tenant's own webhook delivery (e.g., attacker installs the app on a shop they control) remains a byte-for-byte valid signature no matter what `shop-domain`/`topic` header values accompany it. An unprivileged internet user who can trigger webhook events on their own installed shop (or simply replay a captured legitimate delivery) can resend the same signed body while spoofing the `X-Shopify-Shop-Domain` header to any other tenant of the same app. `HmacValidator.validate` will still return `true`, and `Registry.process` will pass the forged `shop` value on to the app's handler as if it genuinely originated from that victim shop — a cross-tenant identity-binding break.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: the `shop` field consumed by the host application (for GDPR-mandatory topics like `customers/redact`, `shop/redact`, `customers/data_request`, or any custom topic) is not covered by the same cryptographic proof that authenticates the payload. This allows cross-tenant event injection/attribution, satisfying the Critical "cross-tenant access" impact bar.

### Likelihood Explanation
Exploitability only requires the attacker to be able to obtain one valid `(raw_body, hmac)` pair — trivially achievable by installing the app for free on their own store (any public Shopify app is installable by any internet user) and capturing one webhook delivery — then replaying it with a forged `shop-domain` header. No access token, `client_secret`, or privileged access is needed.

### Recommendation
Bind the tenant/topic to the signature: include `shop`, `topic`, and `webhook_id` in the material that `to_signable_string`/`HmacValidator` protects (or otherwise cryptographically bind headers to the signed body), and reject any request where the shop asserted in headers cannot be proven to correspond to the signed payload.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (unprivileged, self-serve).
2. Shopify sends the attacker a legitimately signed webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (computed over `B` with the shared `api_secret_key`), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: customers/redact`.
3. Attacker resends the exact same `B`/`H` to the app's webhook endpoint, replacing the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
4. `HmacValidator.validate` recomputes HMAC over `B` only (`to_signable_string` returns `@raw_body`) and it matches `H`, so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to act on/for the victim tenant using attacker-controlled body content. [6](#0-5)

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
