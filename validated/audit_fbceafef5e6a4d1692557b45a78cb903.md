Confirmed the finding: the `Registry.process` flow validates the webhook HMAC over the raw body only, then passes the unauthenticated `shop-domain` header straight into the handler as the tenant identity.### Title
Webhook tenant identity (`shop-domain`) is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the tenant identity (`shop`) used downstream by the host application's handler is taken from an HTTP header that is never part of the signed material. This breaks the identity binding `shop authenticated == shop acted upon`, exactly analogous to the reported ERC-721 issue where a field acted upon (the recipient) was not covered by the safety check that was supposed to protect it.

### Finding Description
`Webhooks::Request#hmac` reads the `hmac-sha256` header, and `#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the signature over `to_signable_string` (the body only) and compares it to the received HMAC using the app's `client_secret`: [3](#0-2) 

`shop` is read from the `shop-domain` header, which is completely outside the signed payload: [4](#0-3) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using `request.shop`, handing the unauthenticated header value to the host application's handler as the trusted tenant identifier: [5](#0-4) [6](#0-5) 

Because the `client_secret` used for the HMAC is shared across every shop that has installed the app, any merchant (an unprivileged, uncontrolled internet-facing tenant of the app) that receives a legitimate webhook from Shopify for their own store possesses a `(raw_body, hmac)` pair that is valid for that body under the app's secret regardless of which `shop-domain` header accompanies it. That merchant can replay the same body/HMAC to the app's public webhook endpoint while substituting the `shop-domain` header (and/or `webhook-id`) for a different, victim shop. `HmacValidator.validate` will accept it because the header is never part of `to_signable_string`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

This is the same bug class as the report: a value that is acted upon by privileged/tenant-sensitive logic (`to`/recipient in the ERC-721 case; `shop` here) is not covered by the verification mechanism meant to guarantee its authenticity (`safeTransferFrom` check / `transferFrom`'s missing receiver check in the report; the HMAC signature here).

### Impact Explanation
This crosses a tenant boundary: it lets one authenticated app-installer (attacker's own shop) inject webhook events that a host application will process as if they belong to a different shop. Depending on how the host app's `WebhookHandler#handle` implementation uses `data.shop` (e.g., to look up or update per-shop records, provision resources, or trigger side effects), this can result in cross-tenant data corruption or cross-tenant actions being taken under another merchant's identity — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate, unprivileged installer of the target app (no special access needed beyond installing the app, which triggers real webhooks), and (2) the ability to send arbitrary HTTP requests to the app's public webhook endpoint with attacker-controlled headers, which is trivial. No access token, `client_secret`, or other privileged material is needed — the attacker only needs a body/HMAC pair they legitimately received for their own shop.

### Recommendation
Bind the `shop-domain` (and other identity-bearing headers such as `webhook-id`/`topic`) into the signed material used for HMAC verification, or otherwise cryptographically bind the shop identity to the signature (e.g., include shop in the signable string, or require host applications to independently verify that `data.shop` corresponds to a shop that legitimately has this webhook subscription/topic registered) before trusting `WebhookMetadata#shop` for tenant-sensitive operations. At minimum, document prominently that `data.shop` in `WebhookHandler#handle` is not covered by the HMAC guarantee and must not be treated as authenticated without additional verification (e.g., cross-checking against the topic's expected callback registration).

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; attacker receives a real webhook POST with raw body `B`, headers including `x-shopify-shop-domain: attacker-shop.myshopify.com` and `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker crafts a new HTTP request to the app's webhook endpoint with the exact same body `B` and `hmac-sha256: H`, but sets `shop-domain: victim-shop.myshopify.com` (and any other desired headers such as `webhook-id`).
3. `Webhooks::Request.new(raw_body: B, headers: forged_headers)` parses successfully (all required headers present).
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and compares to `H` — it matches because the shop header was never part of the signed string: [7](#0-6) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host application processes the attacker-controlled body `B` as though it were a genuine event for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-23)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
```
