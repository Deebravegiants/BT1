## Title
Webhook HMAC signature does not cover the `shop-domain` header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, excluding the `shopify-shop-domain` (and `topic`/`webhook-id`) headers from the HMAC computation. `Utils::HmacValidator.validate` verifies the signature exclusively against this body, and `Webhooks::Registry.process` then hands the handler a `WebhookMetadata` built from the *unauthenticated* `shop` header. This breaks the identity binding `HMAC-signed-bytes == bytes acted on`, letting anyone who possesses one valid `(raw_body, hmac)` pair (trivially obtainable by installing the app on their own store and receiving a real webhook) replay it with an arbitrary spoofed shop domain.

### Finding Description
The HMAC-covered payload is defined as: [1](#0-0) 

while the shop identity used downstream comes from a header that is never part of that signed string: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the body) against the computed HMAC: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust `request.shop` and dispatches it straight to the app-provided handler: [4](#0-3) 

Because Shopify signs webhooks with the app's single `client_secret` (shared across every shop that installs the app, not a per-shop key), the same secret is used to compute the HMAC no matter which tenant sent the webhook. An attacker who installs the app on a shop they control receives real webhooks (e.g. `app/uninstalled`, `customers/data_request`, `orders/create`) with a correctly computed HMAC over the body. Since the shop header is never mixed into that signature, the attacker can resend the exact same `(raw_body, hmac-sha256)` pair to the host application's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (body/HMAC pair is unchanged and valid), and `Registry.process` forwards `shop: <victim-domain>` to the handler — an equality the code never actually checks: `HMAC-verified-origin == shop-acted-on` does not hold.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker-controlled webhook body is processed under an arbitrary victim shop's identity. Depending on the topic and how the host app's `WebhookHandler` uses `WebhookMetadata#shop` (the gem's documented usage pattern — e.g., looking up/mutating the shop's stored session, honoring GDPR `shop/redact` or `customers/redact` mandatory topics, or reacting to `app/uninstalled` to purge session data), this enables an attacker to trigger data deletion, session invalidation, or ingestion of attacker-controlled data under a victim tenant's identity without ever holding that victim's access token or credentials — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is high for any app author using an unmodified installation of the app (which is trivial and requires no privileged access): the attacker only needs to install the target app on their own store to obtain one legitimately-signed `(body, hmac)` pair, then replay it with a forged shop header to the shared webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the HMAC-signed material — or otherwise cryptographically bind the `shop-domain` header to the same signature that authenticates the body — in `Webhooks::Request#to_signable_string`, and have `Registry.process` reject requests where the asserted shop is not verifiably tied to the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers/receives any HTTP webhook (e.g. `orders/create`); Shopify sends `POST /webhooks` with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac over raw body>`, and the raw JSON body.
2. Attacker captures the raw body and its HMAC header unmodified.
3. Attacker resends the identical body and HMAC header to the host app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged request; `Utils::HmacValidator.validate` calls `to_signable_string`, which returns only `@raw_body` — identical to step 1 — so the signature check passes.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's json>, ...)`, and the host application processes attacker-controlled data as if it came from the victim tenant.

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
