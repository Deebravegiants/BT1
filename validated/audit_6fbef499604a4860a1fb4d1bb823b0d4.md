### Title
Webhook `shop-domain` header is trusted for tenant attribution but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its `hmac`/`to_signable_string` over the raw request body only, while the `shop` value used to attribute the webhook to a specific merchant/tenant is read directly from the unauthenticated `X-Shopify-Shop-Domain` header. `Registry.process` validates only that the body's HMAC matches, then passes the unverified `shop` header straight into `WebhookMetadata`, which the host application uses to route/attribute the payload to a tenant.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only [1](#0-0) , and `Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that value [2](#0-1) . `Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` (the body) against `hmac` [3](#0-2) , and then constructs `WebhookMetadata` using `request.shop` taken from the header, unrelated to the signed bytes [4](#0-3) .

The binding that should hold is: `hmac-signed-bytes == bytes that determine tenant identity`. Here it is broken: `hmac-signed-bytes = raw_body` while `tenant-identity = shop-domain header`, an entirely separate, unauthenticated field. As a result, once an attacker (any merchant who has installed the app on their own store, or anyone who intercepts one webhook delivery) is in possession of a single valid `(raw_body, hmac)` pair signed by the app's `client_secret`, they can replay that exact body to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value. The HMAC check still passes (because it verifies the body, not the shop), and `Registry.process` will hand off `WebhookMetadata` claiming to be from any shop, which the host application typically uses to look up per-tenant records/sessions.

### Impact Explanation
If a host application (per the gem's documented contract) uses `WebhookMetadata#shop` to select or scope tenant records — which is the intended purpose of this field — an attacker can cause the app to process attacker-supplied webhook data under a victim shop's identity. This crosses a tenant boundary without any credential belonging to the victim, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any user can install the app for free on their own development/trial store, thereby legitimately receiving one correctly-signed `(body, hmac)` pair from Shopify. They can then replay it against the app's public webhook endpoint with a forged shop-domain header. No possession of `api_secret_key`, access tokens, or victim credentials is required — only reuse of a signature the attacker was legitimately given for their own store. This is a straightforward replay requiring only network access to the public webhook route.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically tie the shop-domain header to the signed payload before it is trusted for routing. At minimum, `Utils::HmacValidator`/`Request` should require the app to independently confirm that `request.shop` corresponds to a shop that legitimately owns the given payload (e.g., by validating shop against an active/known session before processing) rather than trusting the header value outright as tenant identity in `WebhookMetadata`.

### Proof of Concept
1. Install the target app on an attacker-controlled store `attacker-shop.myshopify.com`; trigger any webhook (e.g., `products/create`) to capture a legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair signed with the app's `client_secret`.
2. Replay the exact same `raw_body` and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` succeeds (it only checks the body against the secret) — see [5](#0-4)  and [6](#0-5) .
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(..., shop: request.shop, ...)` using the attacker-forged `victim-shop.myshopify.com` value [7](#0-6) , causing the host app to process attacker data as if it originated from the victim shop.

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
