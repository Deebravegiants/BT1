### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, then trusts the `shop` value taken from the `X-Shopify-Shop-Domain` header — a header that is never included in the signed payload — to build the `WebhookMetadata` passed to the app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the (unauthenticated) header: [2](#0-1) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, i.e. body-only, and compares it via `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` validates only this HMAC and then immediately constructs `WebhookMetadata` using `request.shop`, which is never bound to the signature: [4](#0-3) 

This is exactly the "field acted on but not covered by the HMAC" identity-binding gap: the equality the gem should enforce is `shop_used_by_handler == shop_that_produced_the_signed_body`, but the code only proves `hmac == HMAC(raw_body, secret)`, with `shop` free-floating outside that proof.

### Impact Explanation
Any party who can obtain one genuinely-signed `(raw_body, hmac)` pair for *any* topic/shop (e.g., by installing the app on their own store and capturing a legitimate webhook delivery) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header value naming a victim shop. `HmacValidator.validate` still succeeds (it never looks at the shop header), so `Registry.process` will invoke the registered handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain. Any host application that uses `data.shop` for tenant lookup/session resolution (the documented and expected usage pattern for this gem) will act on that request as if it were an authentic webhook for the victim tenant — a cross-tenant identity-binding bypass.

### Likelihood Explanation
The only prerequisite is possession of one legitimately-signed body for any topic (trivially obtainable by any developer with a test/dev store using the same app, since the HMAC secret is the app's, not tied to any particular shop), plus the ability to send an HTTP POST with attacker-controlled headers to the app's public webhook endpoint. No access token, session, or `client_secret` is required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the value that is HMAC-verified, or otherwise cryptographically bind the `shop` header to the validated payload before it is trusted for tenant routing — e.g., require callers to pass the expected shop and compare it against a separately-authenticated source (such as an already-established session for that shop) rather than trusting the unsigned header value directly in `WebhookMetadata`.

### Proof of Concept
1. Install the app on attacker-controlled store `attacker.myshopify.com`; capture a real webhook delivery, e.g. `orders/create`, noting `raw_body` and its `X-Shopify-Hmac-Sha256` header.
2. Send a POST to the app's webhook endpoint with the identical `raw_body` and HMAC header, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `raw_body` against the secret.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) builds `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and dispatches it to the app's handler, which processes attacker data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L189-200)
```ruby
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
