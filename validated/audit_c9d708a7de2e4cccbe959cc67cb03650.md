### Title
Webhook shop identity is not bound by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but signs only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are parsed straight from unauthenticated HTTP headers. `Registry.process` accepts the request once the body's HMAC checks out and then forwards the header-derived `shop` value to the app's handler as if it were verified, letting an attacker rebind a validly-signed payload to an arbitrary shop.

### Finding Description
`HmacValidator.validate` is invoked on the `Request` object in `Registry.process`: [1](#0-0) 

The HMAC is checked against `to_signable_string`, which returns only `@raw_body`: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are read directly from headers that are never part of the signed material: [3](#0-2) 

The identity binding the code relies on is: `shop authenticated (HMAC over headers+body) == shop used by handler (request.shop from header)`. In reality the equality only holds for `body signed == body received`; the `shop-domain` header is never covered by the signature, so `shop` handed to `WebhookMetadata` is attacker-controllable independent of whether the HMAC passes.

Because the HMAC secret (`Context.api_secret_key`) is the same for every shop installed on a given app, any merchant who installs the app can capture a legitimately-signed webhook body destined for their own store, then replay the identical body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only recomputes the HMAC over `@raw_body`, and `Registry.process` dispatches the handler with the forged `shop`: [4](#0-3) 

### Impact Explanation
Any app that keys business logic in its webhook handler off `WebhookMetadata#shop` (e.g. looking up/mutating a tenant record, feature flags, or app-store license logic by shop domain) can be made to act on behalf of a different, victim shop's identity, purely by an attacker who legitimately installed the app on any shop of their own. This is a cross-tenant identity-binding break driven entirely by data this library treats as trusted context but never actually authenticates.

### Likelihood Explanation
Any developer/merchant who installs the app can trivially obtain a validly-HMAC'd webhook body for their own shop (Shopify sends these automatically), and header replacement in an HTTP request is basic tooling — no secrets, tokens, or privileged access are required beyond having a normal, unprivileged shop account with the app installed.

### Recommendation
Bind `shop` (and ideally `topic`/`api_version`) into the signed material used by `to_signable_string`, or otherwise document/enforce that `Request#shop` must never be trusted without an out-of-band authenticated correlation (e.g., matching against the shop of the session/webhook subscription that was registered), analogous to including the previously-unbound field in the HMAC computation.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture any legitimate webhook Shopify sends, e.g. `orders/create`, including its raw body and its valid `X-Shopify-Hmac-Sha256` header.
2. Replay that exact body/HMAC pair to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `request.hmac` against `OpenSSL::HMAC.hexdigest(..., @raw_body)` — unaffected by the header change — so validation succeeds.
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and performs its shop-scoped logic against `victim.myshopify.com`, even though Shopify never sent this webhook for that shop. [5](#0-4)

### Citations

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
