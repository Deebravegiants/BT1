### Title
Webhook shop-domain identity not covered by HMAC signature enables cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) for an inbound webhook purely from the unauthenticated `X-Shopify-Shop-Domain` header, while the HMAC signature that `Utils::HmacValidator` checks covers only the raw request body. The `shop` value is never part of the signed material, so the binding "HMAC-authenticated request == authenticated for shop X" does not hold. `Registry.process` then hands this unauthenticated `shop` value straight to the app's webhook handler as the tenant key.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the (unauthenticated) HTTP header, independent of the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` header — it never incorporates `shop`: [3](#0-2) 

`Registry.process` validates only this body/HMAC pair, then forwards `request.shop` unchanged to the handler as the tenant identifier: [4](#0-3) 

Because a single app's `api_secret_key` is shared across **every** shop that has installed the app, any merchant who installs the app can trigger events on their own store and receive genuinely Shopify-signed webhook deliveries (valid HMAC over that body). Since the `shop` header is excluded from the signed content, that same attacker can present the identical (body, HMAC) pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `HmacValidator.validate` still returns `true` (the body/HMAC pair is genuinely valid), and `Registry.process` reports the event to the handler with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own store.

This is the same class of defect as the reported bug: a value that influences trust/target decisions (there, the redirect host; here, the tenant/shop identity) is not covered by the verification mechanism that is supposed to bind the request to a specific principal (there, response validation; here, the HMAC signature).

### Impact Explanation
Any app that uses `ShopifyAPI::Webhooks::Registry`/`Request` to route webhook data by `shop` (e.g., writing order/customer/product data into per-tenant storage, or using `shop` to select a stored session/access token) can be tricked by one malicious merchant into writing attacker-controlled data under another store's identity, or into acting on another store's behalf with the wrong data. This is a cross-tenant access/data confusion issue in a multi-tenant SaaS app, which the rules classify as Critical impact.

### Likelihood Explanation
Exploitation requires only an unprivileged attacker who can install the target app on their own (attacker-owned) Shopify store — a routine, unauthenticated action available to any internet user — and the ability to send an HTTP request to the app's public webhook endpoint with a modified header. No access token, `client_secret`, or privileged account is required, matching the "unprivileged internet user" threat model in scope.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) value into the material that is HMAC-verified, or otherwise cryptographically tie the claimed shop to the specific installation/session before trusting `request.shop`. At minimum, the gem should require callers to cross-check `request.shop` against a known, previously-established session/shop record for that installation rather than trusting the header value outright once the (shop-independent) body HMAC passes.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and legitimately triggers a webhook event (e.g., `orders/create`) with attacker-chosen order content.
2. Shopify delivers the webhook to the app's public endpoint with headers including `X-Shopify-Hmac-Sha256: <valid HMAC over raw body>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same raw body and `X-Shopify-Hmac-Sha256` value to the same endpoint but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) succeeds because it only checks `raw_body` against the HMAC.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, causing the host app to process/store attacker data under the victim tenant's identity.

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
