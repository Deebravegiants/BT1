### Title
Webhook `shop-domain` header is not covered by HMAC validation, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value strictly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header, while the HMAC signature that `Registry.process` validates only covers the raw request body. This breaks the identity binding: `shop asserted to the handler == shop bound by the signature` does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from a header that is never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` (which uses `to_signable_string`, i.e. the body only) and then forwards `request.shop` unchanged into the handler metadata: [3](#0-2) 

`HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string`, i.e. the raw body, using the app's single, shop-independent `api_secret_key`: [4](#0-3) 

Because a single app has one `client_secret` shared across every shop that installs it, any store that installs the app can trigger a legitimate webhook and obtain a validly-HMAC-signed raw body. Since `topic`, `shop-domain`, `api-version`, and `webhook-id` headers are not part of the signable string, an attacker who controls the transport (or who can trigger delivery and capture/replay the request, e.g. via a proxy, logging middleware, or a controlled network path to the app's webhook endpoint) can resend that exact body with the `shop-domain` header swapped to a victim shop's domain. `HmacValidator.validate` will still pass because the body bytes are untouched, and the handler will process the payload as if it originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: the gem authenticates the *bytes* of the webhook body but not the *tenant* (`shop`) the app's handler code relies on. A downstream handler that uses `WebhookMetadata#shop` to select which merchant's data/record to update, delete, or query (a normal and expected usage pattern) can be made to act on the wrong tenant's data, using a payload the attacker fully controls except for HMAC compliance (which comes for free from their own store's legitimate webhook). This matches the Critical bar of cross-tenant access.

### Likelihood Explanation
Exploitation requires the ability to intercept or resend an HTTP request destined for the app's webhook endpoint with a modified header — e.g. a merchant/attacker installing the app on their own shop (fully legitimate, no special privilege) to obtain a validly signed webhook body, then replaying it with an altered `shop-domain` header through any point where headers can be rewritten before reaching the gem's `Webhooks::Request.new`/`Registry.process` call (e.g. shared ingress, load balancer, or a compromised/careless reverse proxy in the host app's stack). No `api_secret_key` or access token is needed by the attacker.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the value that is HMAC-verified (Shopify's actual webhook signature only ever guarantees body integrity, so the gem should treat the `shop-domain` header as untrusted unless it can be bound to the verified payload/topic registration), or require callers to cross-check `request.shop` against the shop associated with the specific webhook subscription/registration before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger a real webhook event (e.g. `orders/create`) so Shopify sends a validly HMAC-signed POST to the app's webhook endpoint using the app's `client_secret`.
2. Capture the raw body and `shopify-hmac-sha256` header of that request (attacker fully controls their own shop's webhook payload content).
3. Resend the identical body and HMAC header to the app's webhook endpoint, but replace `shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` in `Registry.process` succeeds because it only checks `@raw_body` against the secret. `handler.handle` is invoked with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content, causing the app to process attacker-controlled data as if it belonged to the victim tenant. [3](#0-2)

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
