### Title
Webhook `shop` identity is taken from an unauthenticated HTTP header not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-verifying the raw request body, but the `shop` value that is handed to the application's webhook handler (used to attribute the event to a specific merchant/tenant) is read directly from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the HMAC computation.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` verifies the HMAC exclusively against this signable string [2](#0-1) . Meanwhile `Webhooks::Request#shop` is derived purely from the `shopify-shop-domain` / `x-shopify-shop-domain` header via `shopify_header` [3](#0-2) [4](#0-3) .

`Registry.process` validates only the HMAC of the body and then forwards `request.shop` straight into `WebhookMetadata`, which is passed to the app's handler as the tenant identifier: [5](#0-4) .

The broken identity binding is:
`hmac_valid(raw_body) == true` should imply `shop == the merchant that produced raw_body`, but in fact `shop` is sourced from an entirely separate, unsigned channel (an HTTP header), so:
`verified(raw_body) ≠ verified(shop)`.

Because the header is not part of the signed material, any two Shopify webhook deliveries that carry byte-identical bodies (which is trivial to obtain — an attacker who owns their own store, or replays a previously observed payload, receives a legitimately signed body+HMAC pair for their own tenant) can be replayed to the target app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to any victim shop domain. `HmacValidator.validate` will still return `true` because it only checks `raw_body`, yet `Registry.process` will dispatch the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
If the host application's webhook handler uses `WebhookMetadata#shop` (as the gem's own API is designed for handlers to do) to look up the corresponding merchant session/access token or to write tenant-scoped state, an attacker can forge the shop attribution of an otherwise validly-signed webhook body and cause the application to process (or store) data under a victim shop's identity — a cross-tenant confusion driven entirely by this gem's failure to bind the `shop` claim into the authenticated payload. This matches the Critical "cross-tenant access" category since the tenant-selecting field is unauthenticated.

### Likelihood Explanation
Exploitation only requires the ability to send arbitrary HTTP requests to the app's public webhook endpoint plus a legitimately-signed body/HMAC pair, which an attacker can obtain cheaply by registering their own development store and capturing its own webhook deliveries (bodies for common topics such as `orders/create` are highly generic/structurally similar or attacker-controllable via their own store's data). No merchant credentials, access tokens, or the app's `client_secret` are needed to mount the header-swap replay itself.

### Recommendation
Bind the `shop` (and other identity-bearing fields such as `topic`, `webhook_id`) into the material that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` value to the verified body (e.g., by having `to_signable_string` include a canonicalized combination of the relevant headers and body, matching what is actually authenticated). At minimum, document and enforce that `WebhookMetadata#shop` must never be trusted for tenant attribution unless independently corroborated (e.g., cross-checked against an already-established session for that shop).

### Proof of Concept
1. Attacker installs the target app on their own development store (`attacker.myshopify.com`) and enables a webhook topic.
2. Shopify sends a legitimately HMAC-signed webhook: body `B`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)`.
3. Attacker intercepts this delivery (they control the receiving webhook URL in step 1, e.g. by pointing it at a proxy they own, or simply reads it from their own endpoint logs) and replays the exact same body `B` and HMAC `H` to the real target app's webhook endpoint, but rewrites the header to `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`= B`) only, and matches `H`, so validation passes [6](#0-5) .
5. The handler executes with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, i.e., the app processes attacker-supplied data as if it originated from the victim shop [7](#0-6) .

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
