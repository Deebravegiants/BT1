### Title
Webhook shop/topic identity spoofing via unauthenticated headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used for tenant routing and dispatch are read from HTTP headers that are never included in the HMAC computation. This breaks the identity binding `shop verified by HMAC == shop used to route/attribute the webhook`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all derived from HTTP headers that are excluded from the signed content: [2](#0-1) 

`Registry.process` verifies the HMAC only, then dispatches to the app's handler using the unauthenticated `request.shop` and `request.topic` values: [3](#0-2) 

`HmacValidator.validate` calls `validate_signature`, which computes the signature strictly over `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header: [4](#0-3) 

Because the `api_secret_key` used to sign webhooks is the same across all shops that install a given app, any merchant/attacker who has legitimately installed the app can trigger a real webhook for their own store, capturing a raw body + valid HMAC pair. They can then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) with a victim shop's domain. The HMAC check in `HmacValidator.validate` still succeeds — it only verifies the body bytes, not the header claiming which shop or topic the payload belongs to. The equality the gem should enforce is `shop bytes covered by HMAC == shop bytes used for tenant dispatch`, but instead `shop` is parsed from an unauthenticated header while only the body is verified.

### Impact Explanation
This enables cross-tenant confusion in the host application: a handler that trusts `WebhookMetadata#shop` (built directly from `request.shop`) to decide which merchant's records to update/delete will act on the wrong tenant's data, using attacker-supplied header values while the cryptographic check only certifies the body. This matches the Critical-impact criterion of cross-tenant access, since the identity binding between the authenticated content and the tenant-identifying header is not enforced by the library itself, and applications relying on the documented `WebhookMetadata` shape to be trustworthy will be exposed.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app onto their own shop (to obtain one valid `(body, hmac)` pair) and be able to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers — both are within the capabilities of an unprivileged internet user/merchant, with no access to `api_secret_key` or any access token required.

### Recommendation
Include the shop domain, topic, and webhook id in the signed/verified material (or otherwise cryptographically bind them to the body) before dispatching, e.g. by validating `x-shopify-shop-domain`/`x-shopify-topic` against a per-shop registered value or by requiring the handler to explicitly cross-check the delivered `shop` against the session it expects, rather than trusting `request.shop` derived purely from an unauthenticated header. At minimum, document clearly that `WebhookMetadata#shop`/`#topic` are not covered by the HMAC guarantee, and encourage consumers to independently authorize the shop before persisting webhook data.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook subscription (e.g. `products/update`) and capture the raw POST body and its `x-shopify-hmac-sha256` value from the delivered request.
2. Replay the exact same body and HMAC header to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com` (and optionally alter `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` (`to_signable_string`) — the check passes because the body/HMAC pair is genuinely valid.
4. The registered handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body:, ...)`, causing the host application to process/store the attacker's own shop data under the victim shop's identity.

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
