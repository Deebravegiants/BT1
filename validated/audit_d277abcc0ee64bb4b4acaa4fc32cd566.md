### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw JSON body, so `Utils::HmacValidator.validate` only ever proves that the *body* bytes were signed with the app's secret. The `shop-domain`, `topic`, and `webhook-id` values come from separate, unsigned HTTP headers and are trusted verbatim by `Registry.process`, which forwards them straight into `WebhookMetadata` handed to the merchant's handler code.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
and `shop`, `topic`, `webhook_id` are read straight from headers that are never part of that signable string: [2](#0-1) [3](#0-2) 

`HmacValidator.validate` only checks the signable string (the body) against the HMAC: [4](#0-3) 

`Registry.process` validates the HMAC once and then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id`, passing them into the handler: [5](#0-4) 

The identity binding the gem is supposed to enforce is: *shop authenticated by HMAC == shop delivered to the handler*. Because the HMAC only covers the body, this equality does not hold — any raw body/HMAC pair that was legitimately produced by Shopify for one tenant (using the app's single, shared `client_secret`) remains a valid HMAC no matter what `shop-domain`/`topic`/`webhook-id` header values are attached to it later.

### Impact Explanation
Any merchant who installs the app (an ordinary, unprivileged tenant with no special access) receives real webhook deliveries signed with the app's secret for their own shop. That merchant can capture one such raw body + HMAC pair and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header changed to point at a different, victim shop. `Utils::HmacValidator.validate` still passes because the signature only covers the JSON body, and `Registry.process` calls the handler with `WebhookMetadata#shop` equal to the attacker-chosen victim shop domain. Any host application that keys its persistence/business logic on `data.shop` — which is exactly the intended and documented usage of `WebhookMetadata` — will process attacker-controlled data as if it came from the victim tenant. This is a cross-tenant confusion/impersonation primitive baked into the gem's own webhook verification logic, not a misuse of the documented API.

### Likelihood Explanation
Requires only that the attacker be a legitimate (unprivileged) installer of the app on their own store — no credential leak, TLS interception, or privileged account needed. Capturing one's own valid webhook deliveries (e.g. via a proxy on the attacker's own endpoint, or from their own store's webhook logs) is trivial, and replaying an HTTP request with a modified header is trivial.

### Recommendation
Include the routing-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material verified by the gem, or otherwise cryptographically bind them to the request before exposing them via `WebhookMetadata`, so `HmacValidator.validate` fails whenever any of these headers are altered relative to what was actually signed by Shopify.

### Proof of Concept
1. App is installed on `attacker.myshopify.com`. Shopify delivers a webhook with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` plus `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures `B` and the HMAC header value.
3. Attacker sends a new HTTP request to the same webhook endpoint with the same body `B` and HMAC header, but `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — this passes because it is only checked against `B`. `handler.handle` is invoked with `WebhookMetadata#shop == "victim.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L30-33)
```ruby
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
