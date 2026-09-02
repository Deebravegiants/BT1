### Title
Webhook `shop`, `topic`, and `webhook_id` headers are trusted but not covered by the HMAC, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`, but the HMAC signature only covers the raw request body — not the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers that the gem hands to the application's handler as "verified" webhook metadata.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  This is the only content that `HmacValidator.validate_signature` checks against the app's `api_secret_key`: [2](#0-1) 

`request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all read straight from unauthenticated HTTP headers: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards these header-derived, unauthenticated fields directly into `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The gem's own documentation instructs developers to treat `data.shop` (and `data.topic`) as verified once `Registry.process` succeeds ("This will verify the request did indeed come from Shopify") and to use it directly to key application data (`shop_domain: data.shop`).

Because Shopify webhook HMACs are signed with the app's `api_secret_key`, which is identical for every shop that has installed the same app, this creates an equality violation: `shop authenticated by HMAC (any shop of this app)` ≠ `shop attributed to the event (request.shop header, unauthenticated)`. A malicious merchant who has installed the target app on their own store receives genuine webhook deliveries with a valid raw body + HMAC signed under the shared app secret. That attacker can then replay the identical `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header to name a victim shop, and/or substituting `x-shopify-topic`/`x-shopify-webhook-id`. `HmacValidator.validate` still succeeds because it only checks the body against the shared secret, and the forged `shop`/`topic` values flow unchanged into the handler.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce: an unprivileged user who is merely a legitimate (if malicious) installer of the app can cause the host application to process webhook data as if it belongs to a different merchant's shop, corrupting cross-tenant records, replaying/duplicating events under another shop's identity, or triggering webhook-driven business logic against a victim tenant. This matches the Critical "cross-tenant access" impact category, since it directly stems from the gem consuming and forwarding an authentication-adjacent field (`shop`) that is not actually bound by the cryptographic check it advertises as sufficient ("verify the request did indeed come from Shopify").

### Likelihood Explanation
Requires only that the attacker be able to install the target app on their own Shopify store (an unprivileged action available to any merchant/developer) and be able to POST to the app's public webhook endpoint with custom headers — no access to `api_secret_key`, access tokens, or any privileged credential is needed. The HMAC secret being shared across all shop installations of a given app is inherent to Shopify's webhook design, making this a straightforward, repeatable exploit path if the host application follows the gem's documented pattern of trusting `data.shop`.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is HMAC-verified, e.g., include `shop-domain`/`topic` in `to_signable_string`, or have `Registry.process` cross-check `request.shop` against an expected/known shop derived from an independently authenticated source (such as looking up the installed shop by an app-specific webhook subscription id) before dispatching to the handler. At minimum, update documentation to explicitly warn that `data.shop`/`data.topic` are not covered by the HMAC and must be independently corroborated by the host application (e.g., against a list of shops that installed the app) before being trusted for tenant attribution.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, obtaining a valid webhook delivery, e.g. for `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker POSTs to the app's public webhook endpoint the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, and `Registry.process` calls `HmacValidator.validate(request)`, which succeeds because `to_signable_string` only checks `B` against `H`: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload actually originated from the attacker's own shop, and the host application (per the gem's documented usage pattern) processes it as data belonging to `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
