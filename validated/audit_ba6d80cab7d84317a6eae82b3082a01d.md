### Title
Webhook cross-tenant spoofing: `shop-domain` header is trusted for tenant routing but not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally forwards `request.shop` to the app's webhook handler as the tenant identifier, without any cross-check that the signed body actually originated for that shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id` and `api_version` are pulled straight from headers and are never part of the signed material: [2](#0-1) 

`Registry.process` validates only the HMAC via `Utils::HmacValidator.validate(request)` (which calls `request.to_signable_string`, i.e. the body only), then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` computes the signature strictly from `verifiable_query.to_signable_string`, confirming the header fields never enter the HMAC input: [4](#0-3) 

The identity binding that should hold is: `(body, secret) → HMAC` == `(shop asserted for that body)`. In this implementation the equality only covers body integrity; the `shop` value used for tenant attribution is never bound into the signed content. Because every shop installing a given app shares the same `Context.api_secret_key`, a user who has legitimate access to one authentic webhook delivery (body + valid HMAC, from their own installed shop) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a different, victim shop. The signature still validates because it only ever covered `@raw_body`, and `Registry.process` hands the forged `shop` straight to the app's handler as the record of which tenant the event belongs to.

### Impact Explanation
This breaks the tenant boundary between merchants sharing the same app installation: an attacker with a genuine webhook delivery for their own shop can inject that payload as if it belonged to an arbitrary victim shop into the app's business logic (e.g., order/customer/webhook handlers that key off `WebhookMetadata#shop`), causing cross-tenant data confusion/injection without needing the target's credentials, access token, or `client_secret`.

### Likelihood Explanation
Exploitation requires only that the attacker control (or have visibility into) one shop with the app installed — no special privilege beyond being a normal merchant/app user, and no access to the app's `client_secret` or another tenant's access token is needed. Capturing/replaying an HTTP request with a modified header is trivial once a valid `(body, hmac)` pair is obtained from the attacker's own installation.

### Recommendation
Bind the shop identity into the material being verified (e.g., include `shop-domain` in `to_signable_string`, or require the host app to independently confirm that `request.shop` corresponds to a shop with a currently valid, previously stored session/access token before acting on the payload) instead of trusting the header purely because the (unrelated) body-only HMAC passed.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g., `orders/create`) and capture the raw POST body plus the `X-Shopify-Hmac-Sha256` header — this HMAC is valid because it is computed only from `@raw_body` and the app's shared `api_secret_key`.
2. Replay the exact same body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) succeeds because the signable string (`@raw_body`) is unchanged.
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body:, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and processes/stores the attacker's data as if it belonged to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
