### Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body. The `shop` value that the library extracts from the `X-Shopify-Shop-Domain` HTTP header and hands to the app's webhook handler as the trusted tenant identity is never included in that HMAC computation. This breaks the intended binding `hmac == HMAC(secret, body)` `⇒` `shop is authentic`, because `shop` is not part of the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`shop` is read from an unauthenticated header, independent of the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC over `to_signable_string` (body only) and then immediately forwards the *unverified* `request.shop` to the app's handler as trusted webhook metadata: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC — for webhooks that string is the body, so the `shop` header is never part of the equality that is verified: [4](#0-3) 

The `api_secret_key` used to compute the webhook HMAC is the app's single client secret shared across **every shop** that has installed the app — it is not shop-specific. A malicious merchant can install the app on their own shop, receive a legitimately-signed webhook (valid `body` + `hmac` pair, computed with the shared app secret), and then replay that exact `body`/`hmac` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. Because the shop field is "acted on" (passed to the handler as the authoritative tenant) but not "covered by the HMAC," the forged request passes `HmacValidator.validate` and the handler processes attacker-controlled body content attributed to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who only controls their own (legitimately installed) shop can make the host application's webhook handler believe an event/body of the attacker's choosing originated from a different merchant's shop. Depending on how the host app keys session/token lookups or business logic off `WebhookMetadata#shop` (which is the library's documented API for identifying the source shop), this can lead to cross-tenant data injection or state corruption for a shop the attacker does not control, without needing the app's `client_secret`, an access token, or any privileged account — satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
Exploitation only requires that the attacker be an ordinary (unprivileged) merchant capable of installing the target app on their own store — a routine, unprivileged action — and capturing one webhook delivery to reuse its body+HMAC with a swapped shop header. No secret material or elevated access is required, and the gem's `Webhooks::Request`/`Registry.process` code path performs no additional binding of shop to signature.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material verified for webhooks, or otherwise cross-check `request.shop` against an independently-trusted source (e.g., require the caller to supply the expected shop for the session being acted on, and compare it against `request.shop` before trusting it) rather than treating the header value as authoritative purely because the body HMAC validated.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (legitimate, unprivileged action).
2. Shopify sends a real webhook to the app's callback URL with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac over body>` and some `body`.
3. Attacker captures this `body` + `hmac` pair.
4. Attacker (or any actor who can reach the app's public webhook endpoint) replays the same `body` and `hmac`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-190`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body against the HMAC (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:12-22`).
6. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the request never originated from, nor was signed specifically for, the victim shop.

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
