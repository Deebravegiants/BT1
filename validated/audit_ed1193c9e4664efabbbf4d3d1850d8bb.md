### Title
Webhook shop-domain header is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are read from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then forwards the unauthenticated `shop` value straight into the handler payload, so a byte sequence that Shopify legitimately signed for one shop can be replayed with a forged `shop-domain` header to impersonate another shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from a header that is never part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only proves that `raw_body` was signed with the app's `client_secret`; it never checks that the `shop` header matches the shop the signature was actually generated for: [3](#0-2) 

`Registry.process` calls this same validator, then immediately hands the caller-supplied, unauthenticated `request.shop` to the app's handler as trusted metadata: [4](#0-3) 

The broken equality is: `shop` value trusted by the handler (`request.shop`, from an unsigned header) should equal `shop` for which Shopify actually generated and signed `raw_body`, but the gem never enforces this equality — it only enforces `HMAC(raw_body, client_secret) == received_signature`. Because Shopify apps use a single, shop‑independent `client_secret` to sign all webhooks, a valid signature over a given `raw_body` remains valid regardless of which shop header is attached to it.

### Impact Explanation
An unprivileged user who owns/administers their own shop installed on the app receives genuine webhook deliveries (with a valid HMAC) to their own endpoint content they control (e.g., an order or product body). By resending that exact captured request to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header rewritten to a victim shop's domain, the HMAC still validates (it only signs the body), and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the victim shop while the body content is attacker-controlled. Any host application that uses `WebhookMetadata#shop` to select the tenant record to update (a standard, documented usage pattern) will write or act on attacker-influenced data under the wrong shop's identity — cross-tenant data injection/confusion.

### Likelihood Explanation
The prerequisites are low-privilege and require no secrets: any user who can install the app on any shop (including their own) can receive at least one legitimately signed webhook and then replay it with a modified header value. No access token, `client_secret`, or privileged access is required.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) in the HMAC-signable content, or otherwise cryptographically bind the shop identity to the signed payload, so `HmacValidator.validate` fails whenever the `shop` header does not match the shop the signature was generated for.

### Proof of Concept
1. Install the app on `attacker.myshopify.com` and trigger a webhook (e.g. create an order) so Shopify sends a genuine, HMAC-signed webhook request to the app's endpoint.
2. Capture the raw request: raw body `B`, and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
3. Resend the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but replacing `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and matches `H` (per `lib/shopify_api/utils/hmac_validator.rb`), so validation passes.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)` (per `lib/shopify_api/webhooks/registry.rb:198-199`), even though the body content originates from the attacker's own shop — demonstrating the shop/body binding is not enforced by the gem.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
