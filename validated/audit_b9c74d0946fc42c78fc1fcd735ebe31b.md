## Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while `shop`, `topic`, `webhook_id` and `api_version` are all taken from unauthenticated HTTP headers. `Registry.process` accepts the request as soon as `HmacValidator.validate` succeeds against the body, then hands the header-derived `shop` straight to the app's handler. This is the same class of bug as the Dex report: a value that is *acted on* (here, the tenant identity, `shop`) is not covered by the cryptographic check that is supposed to authenticate the message, so equality between "the shop the HMAC vouches for" and "the shop the handler believes it is" can be broken.

### Finding Description
`Request#hmac` reads the `hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` verifies only `to_signable_string` (the body) against the `hmac` field: [3](#0-2) 

`Registry.process` performs exactly that check and then dispatches to the app-supplied handler using the header-derived `shop`, `topic`, `webhook_id`, and `api_version`, none of which participated in the HMAC computation: [4](#0-3) 

The broken identity binding, expressed as an equality: the library's contract is `shop_header == shop_that_produced(raw_body, hmac)`. In reality the code only proves `hmac == HMAC(api_secret_key, raw_body)`; it never proves that the specific `shop-domain` header value is the shop for which that `(raw_body, hmac)` pair was actually issued by Shopify. Because the shop identity is carried in a header outside the signed material, any two deliveries destined for the same app (regardless of which shop they belong to) are cryptographically indistinguishable except by the attacker-controlled header.

### Impact Explanation
An unprivileged attacker who can install the target app on their own (attacker-owned) shop receives genuine webhook deliveries with valid, correctly-signed `(raw_body, hmac)` pairs for their shop. Because the header fields are excluded from the signature, the attacker can replay that exact valid body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` (and `topic`/`webhook_id`) header to name a victim merchant. `HmacValidator.validate` still returns `true` (body and HMAC match), so `Registry.process` proceeds and invokes the app's handler with `WebhookMetadata#shop` set to the victim's shop domain. Any app logic that trusts `data.shop` to key per-tenant state, look up the victim's stored session/access token, or drive tenant-scoped side effects is now operating under a forged tenant identity — this is a cross-tenant data/action confusion, matching the "cross-tenant access" impact tier.

### Likelihood Explanation
The only prerequisite is the ability to install the app on any shop (which is generally open to any merchant/attacker for public apps) and the ability to send an arbitrary HTTP request to the app's public webhook endpoint with custom headers — both readily available to an unprivileged internet user. No access token, `client_secret`, or leaked credential is required.

### Recommendation
Bind the tenant identity to the authenticated payload instead of trusting header values that fall outside the HMAC. Either include `shop`, `topic`, and `webhook_id` in the signed material used by `to_signable_string`/`HmacValidator`, or require the consuming application to cross-check the header-derived `shop` against a shop that is already known/registered for this specific webhook subscription (e.g., verify against the shop tied to the stored session before trusting `WebhookMetadata#shop`), and document this requirement clearly since `Registry.process` currently gives no such guarantee.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`, triggering a real webhook delivery with a correctly computed `x-shopify-hmac-sha256` for some `raw_body`.
2. Attacker captures this `(raw_body, hmac)` pair.
3. Attacker sends a POST to the app's webhook endpoint reusing the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and desired `x-shopify-topic`/`x-shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against `hmac` and succeeds [5](#0-4) .
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"`, even though the payload was never issued by Shopify for that shop, demonstrating the cross-tenant identity confusion.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
