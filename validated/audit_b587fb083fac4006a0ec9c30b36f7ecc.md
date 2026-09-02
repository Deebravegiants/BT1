### Title
Webhook `shop-domain` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (tenant identity) used later to process the webhook is read from a separate, unsigned HTTP header. This breaks the equality that should hold between "bytes verified" and "bytes acted on": the HMAC verifies the body, but the tenant-scoping decision is made from a header outside that signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed content: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, so it never touches the `shop` header: [3](#0-2) 

`Registry.process` accepts any request that passes this HMAC check and then dispatches to the app's handler using `request.shop` as the tenant identity, without any additional binding between the verified body and the claimed shop: [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that installs the app (it is not per-shop), any merchant who has installed the app can legitimately obtain a valid `(raw_body, hmac)` pair for their own shop — e.g. by registering an additional webhook subscription pointed at infrastructure they control, using their own Admin API access, and triggering an event. Since the `shop-domain` header carrying tenant identity is never part of the signed content, that same valid `(raw_body, hmac)` pair can be replayed against the target app's webhook endpoint with the `shop-domain` header rewritten to an arbitrary victim shop. `HmacValidator.validate` will still pass (the body and secret are unchanged), and `Registry.process` will hand the attacker-controlled body to the app's webhook handler tagged as if it came from the victim shop.

This is the equality break: the library treats `hmac(secret, raw_body) == received_hmac` as sufficient proof that `(shop, raw_body)` originated from Shopify for that shop, when in fact only `raw_body` is proven.

### Impact Explanation
This allows cross-tenant data/event injection: an unprivileged merchant who has merely installed the app can forge processed webhook events "from" any other shop using the app, feeding attacker-chosen (but validly-signed for a different topic/shop) payloads into the app's per-shop business logic (e.g. order/product/customer sync, GDPR compliance webhooks, uninstall handling). Depending on how the host app keys its logic off `WebhookMetadata#shop`, this can corrupt another merchant's data or trigger tenant-scoped side effects without any credential belonging to that victim shop — a cross-tenant boundary violation.

### Likelihood Explanation
Requires only that the attacker be a legitimate (unprivileged) installer of the same app — no access to the target shop's credentials, no TLS interception, and no possession of the app's `client_secret` is needed. The attacker only needs to capture one valid `(body, hmac)` pair from their own installation and replay it with a different `shop-domain` header, which is realistic for any app accepting third-party installs.

### Recommendation
Bind the shop identity into the verified signable content, or otherwise cryptographically tie the `shop-domain` header to the specific webhook delivery (e.g., include shop/webhook-id in the HMAC input, or reject/require correlation against a per-shop webhook-id registered via the GraphQL API before dispatch), rather than trusting an unsigned header for tenant routing.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and, using their own valid access token, registers a second webhook subscription for a topic (e.g. `products/update`) pointing at a server they control.
2. Attacker triggers the event on their own store; Shopify delivers `POST` with body `B` and header `X-Shopify-Hmac-SHA256: H = HMAC(api_secret_key, B)` to the attacker's server.
3. Attacker sends `POST` to the target app's real webhook endpoint with the same body `B`, same `X-Shopify-Hmac-Sha256: H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds, then dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` to the app's handler, which now processes attacker-controlled data as authoritative for the victim shop.

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
