### Title
Webhook shop-domain identity spoofing via HMAC validation that only covers the request body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, but the `shop` identity that is subsequently handed to the app's webhook handler is taken from an HTTP header that is not included in the signed data. This breaks the intended binding `hmac-authenticated request == request acted upon`, specifically for the shop/tenant identity field, allowing a valid signature from one shop to be replayed with a forged shop-domain for a different shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed string: [2](#0-1) 

`HmacValidator.validate` only checks `to_signable_string` (i.e., the body) against the secret; it never verifies that the `shop` header used downstream is the same shop the signature was actually generated for: [3](#0-2) 

`Registry.process` gates the whole request on this HMAC check and then forwards `request.shop` (the unauthenticated header) straight into `WebhookMetadata`, which the host application's handler uses as the tenant identity: [4](#0-3) 

This is directly analogous to the reported `DivReducer` bug pattern: a check is performed (`_hasValidParentNodeDefinitions` / `HmacValidator.validate`) but the result does not actually gate the field that matters (parent validity / shop identity). Here, the code checks "is this body correctly signed with our secret" but treats that as proof of "this body came from shop X," when `shop` is never bound into the signature at all.

Because the app's `client_secret` is shared across every shop that installs the app, any merchant who installs the app on their own store receives genuine webhooks with valid HMACs (computed with the real, shared secret). That merchant can capture a `(raw_body, hmac)` pair from their own legitimate webhook traffic and replay it to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (the body+secret pair is valid), and `Registry.process` passes the attacker-chosen `shop` value to the handler as though it were authenticated.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as documented/intended by this gem) to look up or act on a specific tenant's data — e.g., to load that shop's session/access token or to update per-shop state — an attacker-controlled shop value lets a malicious merchant impersonate another shop within the webhook processing pipeline. This is a cross-tenant confusion vector rooted directly in this gem's `Webhooks::Request`/`Registry` implementation, not in host misuse of an undocumented feature: the gem presents `WebhookMetadata.shop` as a trusted, verified field to the handler once `HmacValidator.validate` succeeds.

### Likelihood Explanation
Medium: it requires the attacker to be a legitimate merchant of the same app (able to receive real, validly-signed webhooks) and requires the host app to key tenant-scoped logic off `WebhookMetadata#shop`. No secret key, access token, or privileged access is needed — only routine app installation as any shop, which is available to any unprivileged internet user who installs the app on a store they control.

### Recommendation
Bind the shop identity into the signed material or otherwise cryptographically tie it to the authenticated body — e.g., include the shop domain in `to_signable_string`, or have `Registry.process` cross-check the `shop` header/topic pairing against Shopify's known webhook delivery metadata rather than trusting an unauthenticated header once the body HMAC passes. At minimum, document clearly (and enforce in code) that `WebhookMetadata#shop` is not itself HMAC-verified, and validate it against expected/registered shops before using it to scope any tenant-specific operation.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: `raw_body = '{"id":1}'`, `hmac = valid_hmac(raw_body, client_secret)`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with the same `raw_body` and `hmac`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Webhooks::Request.new` builds successfully (all required headers present), `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and matches — validation passes: [4](#0-3) 
4. The handler receives `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)` even though the signature was never generated for `victim.myshopify.com`, giving the attacker control over the tenant identity used by the app's webhook logic.

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
