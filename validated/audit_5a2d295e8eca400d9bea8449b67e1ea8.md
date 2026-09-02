## Title
Webhook Cross-Tenant Shop Spoofing via HMAC Signature That Does Not Cover the Shop Domain — (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the payload to the app's handler tagged with the shop domain taken from the `X-Shopify-Shop-Domain` HTTP header. That header is never included in the signed bytes, so the "shop" identity used to route/attribute the webhook is not bound to the same secret that authenticates the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor reads directly from the (attacker-supplied, unauthenticated) HTTP header and is never part of the signed data: [2](#0-1) 

`Registry.process` validates only the HMAC-vs-body binding via `Utils::HmacValidator.validate(request)`, and then uses the unauthenticated `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` header — since `to_signable_string` is just the raw body, the shop-domain header is outside the binding entirely: [4](#0-3) 

The identity binding broken is: `shop authenticated == shop used to attribute/act on the payload`. Here, the shop that is cryptographically bound (none — the body's HMAC says nothing about which shop it's for) is not equal to the shop actually stored/acted upon (`request.shop`, read from an unauthenticated header). Because a single app shares one `api_secret_key` across every merchant/tenant that installs it, a `(body, hmac)` pair legitimately produced for one shop (e.g., the attacker's own store, which they can freely install the app on and trigger real webhooks from) remains a valid HMAC for that same body when replayed with a different `X-Shopify-Shop-Domain` header value. The gem will accept it and hand the (attacker-controlled) body to the handler tagged as coming from the victim shop.

### Impact Explanation
This is a cross-tenant confusion vulnerability: an unprivileged attacker who operates their own shop with the target app installed can capture a legitimately-signed webhook payload and replay it against the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header, causing the host application to process/store attacker-controlled webhook data as if it originated from a shop the attacker does not control. Depending on how the host app uses `WebhookMetadata#shop` (e.g., as a lookup/tenant key for updating local records), this can result in cross-tenant data corruption or unauthorized cross-tenant data injection — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Any developer using the gem's documented `ShopifyAPI::Webhooks::Registry.process(request)` flow with `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` (exactly as shown in the gem's own tests) is affected, since the vulnerability is in the gem's HMAC-verification/shop-binding logic itself, not a misuse of the API. The only precondition is that the attacker can install the target app on a shop they control (a normal, unprivileged action) to obtain one valid `(body, hmac)` pair, which requires no access to `api_secret_key` or any privileged credential.

### Recommendation
Bind the shop domain (and other identity-relevant headers such as topic/webhook-id) into the signed material verified during webhook processing, or otherwise cross-check `request.shop` against an independently authenticated source (e.g., verify the shop is one the app has an active, previously-established session/installation for) before dispatching to handlers. At minimum, document that `request.shop` is unauthenticated and must not be trusted as a tenant boundary unless additionally verified by the host app.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers any webhook subscription (e.g., `products/update`), receiving a legitimate `raw_body` and a valid `X-Shopify-Hmac-Sha256` computed with the app's shared `client_secret`.
2. Attacker sends this exact `raw_body` and `hmac` header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, raw_body) == hmac` — this succeeds because the body/hmac pair is unmodified: [5](#0-4) 
4. The handler is invoked with `shop: request.shop` equal to `"victim-shop.myshopify.com"` and the attacker-originated body, despite the request never having been authenticated for that shop: [6](#0-5)

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
