### Title
Webhook HMAC signature does not cover the `shop`, `topic`, `webhook_id` and `api_version` fields it authenticates, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop, topic, webhook id and API version solely from unsigned HTTP headers, while its `to_signable_string` (used by `Utils::HmacValidator.validate`) only covers the raw request body. `Registry.process` trusts these unsigned header values (particularly `shop`) and hands them to the app's webhook handler as authoritative tenant identity. This breaks the equality that should hold: *shop authenticated by HMAC == shop acted on by the handler*.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version`, however, are read directly from HTTP headers and are never part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `to_signable_string` (the body): [3](#0-2) 

`Registry.process` checks only this body-bound HMAC, then immediately trusts `request.shop` and `request.topic` (unsigned headers) to build the `WebhookMetadata` passed to the handler: [4](#0-3) 

Because the app's `client_secret` (`Context.api_secret_key`) is shared across every shop that has the app installed, an unprivileged internet user who installs the app on a shop they control can trigger a real webhook (e.g. `orders/create`) and legitimately obtain a genuine `(raw_body, hmac)` pair signed by Shopify. Since the HMAC never binds to the `shop-domain`, `topic`, or `webhook-id` headers, the attacker can then replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting a victim tenant's `x-shopify-shop-domain` header (and/or a different registered topic). `HmacValidator.validate` still succeeds because it only checks the body bytes against the signature, so `Registry.process` dispatches attacker-controlled event data to the handler under `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`.

This is the same class of bug as the RocketTokenRETH report: a value that downstream code treats as authenticated/consistent (the tenant identity conveyed by `shop`/`topic` headers) is not actually covered by the cryptographic check (`hmac` over body only), so an attacker can present authenticated bytes for one context and unauthenticated bytes (headers) for a different context, and the mismatch is never detected.

### Impact Explanation
This enables cross-tenant webhook injection: an attacker-controlled shop's legitimately-signed webhook payload can be replayed against the app while being falsely attributed to another merchant's shop. Any host application logic that keys webhook side effects (data mutation, session/access-token lookups, order/customer record updates, compliance actions such as `customers/redact`) off `WebhookMetadata#shop` will process attacker-supplied data as if it originated from the victim tenant — a cross-tenant access/data-integrity violation.

### Likelihood Explanation
Exploitation requires only: (1) the attacker owns or controls a shop with the target app installed (freely obtainable via any Shopify dev/partner store), (2) knowledge of the app's public webhook endpoint (standard, since Shopify webhook endpoints are unauthenticated by design and rely solely on HMAC), and (3) the ability to send a raw HTTP POST with forged headers to that endpoint. No access token, `client_secret`, or privileged credential is needed.

### Recommendation
Bind the tenant/topic identity into the signed material actually verified, or otherwise cryptographically tie the `shop-domain`/`topic`/`webhook-id` headers to the request before trusting them: e.g., include these header values in `to_signable_string`, or validate that the `shop` header corresponds to a shop that Shopify's HMAC-covered body content actually references, and require the resource IDs embedded in the webhook body to belong to the claimed shop before invoking handlers.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger an `orders/create` webhook to capture a legitimate `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared `client_secret`.
2. POST that identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` and `x-shopify-topic: orders/create`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks the body against the signature: [5](#0-4) 
4. `Registry.process` invokes the registered handler with `WebhookMetadata(shop: "victim.myshopify.com", topic: "orders/create", body: <attacker-controlled JSON>)`, causing the host app to process attacker data as belonging to `victim.myshopify.com`.

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
