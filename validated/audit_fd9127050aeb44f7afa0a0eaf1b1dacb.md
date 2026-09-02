### Title
Webhook Shop/Topic Identity Not Bound to HMAC, Allowing Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw HTTP body, then trusts the `shop` and `topic` values taken from separate, unauthenticated HTTP headers to route and label the payload. Because those identity fields are never included in the signed data, they can be freely substituted on any request that carries a legitimately-signed body, breaking the intended binding `hmac_signed(shop, topic, body) == hmac_signed(body)`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`shop` and `topic` are pulled straight from headers with no cryptographic tie to the body: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate`, which in turn calls `to_signable_string` (the raw body only) and hex-compares it against the secret-derived signature: [3](#0-2) [4](#0-3) 

Once the body's HMAC checks out, `process` immediately hands the *unauthenticated* `request.shop` and `request.topic` to the handler as if they were verified: [5](#0-4) 

The equality the gem should guarantee is: `shop_used_by_handler == shop_that_was_actually_cryptographically_authorized_by_the_HMAC`. In reality the HMAC only authorizes the body bytes, while `shop`/`topic` are attacker-controllable headers on any raw HTTP request the caller crafts, so the equality does not hold.

### Impact Explanation
Any merchant can install the app on their own store (an unprivileged action) and receive a real webhook delivery for that store, giving them a body + valid HMAC pair signed with the app's shared secret. Because the shop/topic headers are outside the signed data, that same (body, HMAC) pair remains "valid" per `HmacValidator.validate` when replayed directly to the app's webhook endpoint with a different `X-Shopify-Shop-Domain` (or topic) header. If the host application trusts `WebhookMetadata#shop` (as this gem's own API design encourages, since it's presented as already-authenticated data after `process` succeeds) to attribute or persist data per tenant, the attacker can cause data to be processed under a victim shop's identity — a cross-tenant confusion originating in this gem's own HMAC-to-identity binding, not merely host-app misuse of a documented caveat.

### Likelihood Explanation
Requires no leaked secret, no TLS interception, and no privileged account — only the ability to install the app once as a normal merchant (to obtain a valid body/HMAC pair) and send a crafted HTTP request with altered headers to the app's own public webhook URL, which is by design internet-reachable.

### Recommendation
Have `Webhooks::Request#to_signable_string` (or `HmacValidator`) fold `shop`, `topic`, and other routing-relevant headers into the signed material actually verified, or otherwise cryptographically bind them (e.g., derive/verify shop membership from the merchant's stored offline access token/session rather than trusting the header) before they are handed to `handler.handle`.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; Shopify sends a real webhook: body `B`, header `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same `B` and `H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this still passes.
4. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ...))` is invoked, causing the host app to process attacker-controlled data under the victim's tenant identity.

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
