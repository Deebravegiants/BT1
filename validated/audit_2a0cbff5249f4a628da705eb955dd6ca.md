Based on the investigation, I found a concrete analog to the reported bug class in `ShopifyAPI::Webhooks::Request` / `ShopifyAPI::Webhooks::Registry`.

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are trusted for tenant routing but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers that are excluded from the HMAC computation. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then hands `request.shop` (an unauthenticated header value) straight to the app's handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
only `@raw_body` is fed into the HMAC check. The `shop`, `topic`, and `webhook_id` accessors instead read directly from headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates only the body-bound HMAC via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to build the `WebhookMetadata` passed to the app-supplied handler: [3](#0-2) 

`HmacValidator.validate` (and `validate_signature`) confirms only that `to_signable_string` matches the HMAC — i.e. only the body bytes are authenticated, not the header-derived `shop`/`topic`/`webhook_id`: [4](#0-3) 

This breaks the intended identity binding `hmac(body) == hmac(body)` is treated as if it proved `shop_header == originating_shop`, when in fact `shop` is a field acted on but not covered by the HMAC. An unprivileged internet user who legitimately operates their own Shopify store (an "unprivileged" actor with no access to the app's `client_secret`/access tokens) receives real, validly-HMAC-signed webhook deliveries for their own shop from Shopify. Because the signature covers only the body, that exact `(body, hmac)` pair remains valid no matter what `shop-domain`, `topic`, or `webhook-id` header values are sent alongside it. The attacker can POST the same body+HMAC to the target app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header (and/or `topic`/`webhook-id`), and `Registry.process` will accept it as authentic and dispatch it to the handler labeled as coming from the victim shop.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) from a successfully-validated `Registry.process` call to select which tenant's data to look up or mutate is exposed to cross-tenant webhook injection: an attacker-controlled shop can cause the app to execute a real webhook payload under an arbitrary victim shop's identity. This matches the Critical "cross-tenant access" impact category since the tenant boundary that the HMAC is meant to protect is not actually bound by it.

### Likelihood Explanation
Any merchant/developer who can install the target app on their own store (a normal, unprivileged action) can capture a real signed webhook and replay it with a forged `shop-domain` header to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is required, only network access to the app's public endpoint and a real webhook delivered to their own shop.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string / HMAC computation (or otherwise cryptographically bind them, e.g. by validating them out-of-band against the registered endpoint's expected shop), so `Utils::HmacValidator.validate` cannot pass unless the header-derived routing fields match what Shopify actually signed.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook event (e.g. `orders/create`), capturing the raw request body `B` and the valid `X-Shopify-Hmac-Sha256: H` header Shopify computed over `B`.
2. Attacker POSTs to the app's public webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`), but `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` returns `B` only. [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` and, if it uses `shop` to scope data access/mutation, performs the action against the victim tenant using attacker-supplied event data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
