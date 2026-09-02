### Title
Webhook `shop` (and other) headers are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop-domain` header (along with `topic`, `webhook-id`, and `api-version`) is never included in the signed material, yet it is trusted verbatim and handed to the host application's handler as the tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e. the body) against `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` performs this single check and then constructs `WebhookMetadata` using the unauthenticated `request.shop`, passing it directly to the host app's handler as the trusted tenant identity: [4](#0-3) 

The identity binding that is broken is: `shop attributed to the webhook` ≠ `shop actually covered by the HMAC-verified bytes`. The only thing proven authentic is the body; the shop header is out-of-band and mutable by anyone who can reach the app's HTTP endpoint.

### Impact Explanation
Any unprivileged actor who can obtain one genuine `(raw_body, hmac)` pair signed with the target app's `client_secret` — trivially achievable by installing the app (even a free/trial install) on their own store and capturing a webhook Shopify sends them — can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will still pass (it only checks the body), and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the victim's domain. Any host application relying on the gem's webhook trust boundary (i.e., "if HMAC validates, the whole `WebhookMetadata` — including `shop` — is authentic") will process forged data as if it originated from another merchant's shop. This is a cross-tenant confusion/injection vector, matching the Critical "cross-tenant access" impact bucket, since attacker-controlled webhook payloads (up to the JSON structure the attacker's own installation legitimately triggered) get attributed to an arbitrary victim tenant.

### Likelihood Explanation
Likelihood is moderate-to-low in practice: the attacker needs the webhook endpoint to be reachable directly (not gated behind additional shop-domain-bound routing by the host app) and needs the forged payload's JSON body (which is fixed to whatever body the attacker's own account legitimately received) to still be meaningful/dangerous when misattributed to the victim shop. No secret material, TLS interception, or privileged account is required — only the ability to install the target app on one's own free Shopify store, which is available to any unprivileged internet user.

### Recommendation
Bind the shop (and ideally topic/webhook-id/api-version) into the HMAC-verified material, e.g. by requiring host applications to additionally correlate `request.shop` against the shop associated with the specific `webhook_id`/session before trusting it, or by documenting explicitly that `shop`, `topic`, etc. are unauthenticated and must be independently validated by the consuming application against known/expected tenants before use.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) so Shopify delivers a legitimately HMAC-signed request to the app's webhook endpoint.
2. Attacker captures the raw body and the `X-Shopify-Hmac-Sha256` header from that delivery — both are valid because they were produced by real Shopify infrastructure using the app's actual `client_secret`.
3. Attacker crafts a new HTTP POST to the same app endpoint using the captured `raw_body` and `hmac` header unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` [1](#0-0) .
5. The handler is invoked with `WebhookMetadata.new(..., shop: request.shop, ...)` where `shop` is `"victim-shop.myshopify.com"` [5](#0-4) , causing the host application to process attacker-controlled webhook data as if it came from the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
