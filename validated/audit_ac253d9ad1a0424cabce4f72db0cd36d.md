### Title
Webhook `shop` (and `topic`) header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop` (and `topic`) values that the request-handling code actually acts on are taken from separate, unauthenticated HTTP headers that are never included in the signed payload. An attacker who is able to obtain any single valid `(raw_body, hmac)` pair for the configured app (for example, by installing the app on their own store and receiving one legitimate webhook) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and/or `shopify-topic`) header. The library will treat the forged request as authentic and hand it to the app's handler tagged with the attacker-chosen shop, breaking the binding between "bytes verified by HMAC" and "shop identity acted upon."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are read straight from HTTP headers with no cryptographic linkage to the signed body: [2](#0-1) 

`Registry.process` validates the webhook using `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (i.e. the raw body) against the HMAC header, then immediately forwards `request.shop` (and `request.topic`) — both unauthenticated — to the registered handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` computes the signature purely from `verifiable_query.to_signable_string`, confirming that for webhook requests the `shop` header plays no role in the signature: [4](#0-3) 

Because the HMAC secret (`api_secret_key`) is shared across all shops that install a given app, and the signable string is only the raw body, any `(body, hmac)` pair that was ever valid for the app remains valid for the app regardless of which shop header accompanies it. This breaks the intended identity equality `hmac-authenticated body == shop the body is attributed to`; the library only proves "this body was signed by our app secret at some point," not "this body was sent for this shop."

### Impact Explanation
An unprivileged user who can get the app to deliver them one legitimate webhook (e.g., by installing the app on a free/trial store they control, or simply observing any of the app's mandatory webhooks like `customers/data_request`) obtains a `(raw_body, hmac)` pair that passes `HmacValidator.validate` for the app for eternity (until key rotation). By replaying that pair to the app's public webhook endpoint with a forged `shopify-shop-domain` header pointing at a victim shop, they cause `Registry.process` to invoke the app's handler with `WebhookMetadata` claiming that data belongs to the victim shop. Depending on how the host application's handler uses `shop` (typically to look up the shop's session/access token and write data, invalidate caches, or perform admin actions scoped to that shop), this enables cross-tenant data injection/corruption or spoofed lifecycle events (e.g., forging `shop/redact` or `customers/redact` for a shop the attacker does not own), which qualifies as cross-tenant access.

### Likelihood Explanation
Exploitation requires no privileged credentials, access tokens, or `api_secret_key` knowledge — only the ability to receive one legitimate webhook from the target app (trivial for any developer who installs the app on their own store) and to send an HTTP POST to the app's already-public webhook endpoint with custom headers, which any internet user can do. This is a realistic, low-effort attack path.

### Recommendation
Include the tenant-identifying and topic fields (`shop`, `topic`, and ideally `webhook_id`/timestamp) in the HMAC-signed payload verification, or otherwise cryptographically bind them to the raw body before trusting them (e.g., verify that the `shop` header matches a shop that is expected/known to the app for the delivered webhook_id, or require Shopify's newer verification mechanisms that scope the signature per delivery). At minimum, document that consuming applications must not trust `request.shop`/`request.topic` for authorization decisions without additional verification, since only the raw body is currently authenticated.

### Proof of Concept
1. Install the target app on an attacker-controlled trial shop `attacker.myshopify.com`; trigger any webhook topic registered by the app (e.g. `customers/data_request`) and capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — this pair is valid because it was signed with the app's `api_secret_key`.
2. Replay the exact same body and HMAC header to the app's webhook endpoint, but replace the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (`lib/shopify_api/webhooks/request.rb:45-63`), and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates the HMAC (which only checks the raw body) and then calls the handler with `shop: "victim-shop.myshopify.com"`, even though that body/event never originated from the victim shop.

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
