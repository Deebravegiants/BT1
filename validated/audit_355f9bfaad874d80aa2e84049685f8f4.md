## Title
Webhook HMAC validation does not bind the `shop` field, allowing cross-tenant shop-domain spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values are read from unauthenticated headers and passed unchecked to the webhook handler. Any internet user who can obtain one legitimately-signed webhook delivery (e.g. by triggering a webhook on a shop they themselves control/installed the app on) can replay that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header, and `HmacValidator.validate` will still accept it.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate_signature` only verifies the signable string (the body) against the received HMAC: [3](#0-2) 

`Registry.process` checks only the HMAC and then dispatches to the handler using the unauthenticated `request.shop`: [4](#0-3) 

The identity binding that is broken is:
`HMAC-verified bytes (raw body)` ≠ `shop identity acted upon (request.shop header)`.

Because the shop header sits outside the signed content, the equality "shop that produced this signed payload == shop the handler believes it came from" does not hold. An attacker who legitimately installs the app on their own shop can capture a real `(raw_body, x-shopify-hmac-sha256)` pair delivered by Shopify to their own endpoint, then POST that exact pair directly to the app's public webhook URL with `X-Shopify-Shop-Domain` changed to a victim shop. `HmacValidator.validate` recomputes the HMAC over `raw_body` only, finds it matches, and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This crosses a tenant boundary using only unprivileged, self-service capability (installing the app on any shop, which is normal for legitimate merchants including attacker-controlled test shops) — no `api_secret_key`, access token, or privileged account is required. Depending on how the host application's webhook handlers key off `shop` (session lookup, `app/uninstalled` cleanup, GDPR `customers/redact`/`shop/redact` processing, billing/subscription state, cache invalidation, etc.), this enables cross-tenant actions/state corruption attributed to a shop the attacker does not own, satisfying the High-impact category of "credential/tenant binding bypass" style issues described in scope.

### Likelihood Explanation
Exploitation requires only: (1) installing the app on an attacker-controlled shop to receive one authentic webhook (routine, unprivileged action any Shopify merchant/developer can do), and (2) sending a single crafted HTTP POST to the target app's public webhook endpoint with a modified `Shop-Domain` header and the captured, still-valid body/HMAC pair. No secrets, tokens, or elevated access are needed, making this practically reachable by any unprivileged internet user who can reach the webhook endpoint.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed material that `HmacValidator` verifies, or otherwise cryptographically bind the shop domain to the payload before it is trusted (e.g., verify the shop against a previously stored, authenticated session rather than trusting the header at dispatch time). At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted without an independent shop verification step by the host application.

### Proof of Concept
1. Install the app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic (e.g. `products/create`) and capture the resulting request: `raw_body` and `X-Shopify-Hmac-Sha256` header (both genuinely signed by Shopify with the app's `api_secret_key`, but note `api_secret_key` itself is never learned by the attacker).
2. Send a new POST request directly to the app's public webhook endpoint with:
   - Same `raw_body`
   - Same `X-Shopify-Hmac-Sha256` value
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic` unchanged (or any registered topic)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which succeeds because it only checks the body hash [5](#0-4) , then invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [6](#0-5) , causing the host application to process attacker-supplied content as if it came from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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
