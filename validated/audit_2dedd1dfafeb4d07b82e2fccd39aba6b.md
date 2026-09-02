### Title
Webhook shop identity spoofing via HMAC signature that covers only the request body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string from the raw body only, while the tenant-identifying `shop` field is read from an unsigned HTTP header. `Registry.process` trusts this header value as the authoritative shop identity when dispatching to the app's `WebhookHandler`, breaking the intended binding `hmac_covers(shop) == true`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that value [2](#0-1) . `Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` (the body) using `Context.api_secret_key` [3](#0-2) ; the header carrying the shop is never part of the signed material. `Registry.process` then checks only `Utils::HmacValidator.validate(request)` and, if it passes, builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from that unauthenticated header and hands it to the app's handler [4](#0-3) .

Because `api_secret_key` (the app's `client_secret`) is shared across every merchant that has installed the app, any merchant who has legitimately installed the app can obtain a genuine `(body, hmac)` pair for their own shop from a real Shopify-delivered webhook. That attacker-controlled merchant can then replay the identical body and HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim shop's domain). The signature check still succeeds because the header is not covered by the HMAC, so `Registry.process` invokes the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop.

### Impact Explanation
This is a cross-tenant identity-binding break: the equality `hmac_signed_shop == dispatched_shop` does not hold. Any app whose webhook handler uses `WebhookMetadata#shop` to select which merchant's data/session to act on (a documented and expected usage pattern of `WebhookHandler#handle`) can be made to perform actions attributed to, or modify state belonging to, a different tenant than actually sent the request — i.e., cross-tenant access driven entirely by data this gem hands the host application as trusted/verified.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even free/trial) installer of the target app on their own shop, letting them harvest one valid `(raw_body, hmac)` pair, then send a crafted HTTP request to the app's public webhook endpoint with a spoofed shop header. No access to `api_secret_key`, tokens, or victim credentials is needed, and the request passes the gem's own `HmacValidator.validate` check, so it is straightforward for any unprivileged app-installer to attempt.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically verify it: e.g., include the shop domain in the HMAC computation, or cross-check the header's shop domain against the shop actually returned/expected by Shopify's delivery for that specific installation before constructing `WebhookMetadata`. At minimum, document prominently that `Webhooks::Request#shop` is unauthenticated and must not be trusted for tenant-sensitive decisions without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a legitimate webhook (e.g., `orders/create`) to the app's endpoint with a valid `x-shopify-hmac-sha256` header computed over the JSON body using the app's shared `api_secret_key`.
2. Attacker captures `raw_body` and the corresponding `hmac` header value.
3. Attacker resends the identical `raw_body` and `hmac` header to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds (it only checks the body) [5](#0-4) , and `Registry.process` calls the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` [4](#0-3) , causing the app to act as if the webhook originated from the victim shop.

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
