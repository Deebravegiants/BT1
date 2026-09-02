Based on my research, the strongest in-scope analog to the reported bug class ("a field trusted for a security-critical operation without being properly bound/verified") is the webhook `shop` (and `topic`) header not being covered by the HMAC signature in `ShopifyAPI::Webhooks::Request` / `ShopifyAPI::Webhooks::Registry`.

### Title
Webhook `shop-domain` (and `topic`) header is trusted for tenant attribution but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (and `topic`) values consumed downstream come from HTTP headers that are never included in the HMAC-signed material. `ShopifyAPI::Webhooks::Registry.process` validates only the body's signature and then blindly forwards the unauthenticated `shop` header to the app's handler as the tenant identifier.

### Finding Description
`Request#hmac` reads `shopify-hmac-sha256` and `Request#shop` reads `shopify-shop-domain`/`x-shopify-shop-domain`, both plain headers with no cryptographic binding to each other: [1](#0-0) 

The signable string used for HMAC verification is only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then passes the unauthenticated `request.shop` (and `request.topic`) straight into the handler as the tenant context: [3](#0-2) 

Because the signature never binds `shop` (or `topic`/`webhook_id`/`api_version`) to the body, the equality the code implicitly assumes — "the shop whose secret signed this body" == "the shop attributed by the `shop-domain` header" — does not actually hold. Anyone who possesses one genuinely-signed webhook body+HMAC pair (e.g., from their own shop, which legitimately receives real Shopify webhooks once the app is installed on it) can replay that exact body+HMAC to the app's endpoint while substituting a different `shop-domain` header value. `HmacValidator.validate` will still succeed because it only checks the body against the signature, and the handler will receive the forged `shop` value as if it originated from a different tenant.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as returned by this gem) to select which tenant/session record to look up or mutate — the documented and expected usage pattern — an attacker who controls one legitimate, installed shop can forge webhook deliveries attributed to an arbitrary victim shop domain, causing the app to process attacker-controlled body content under a victim tenant's identity. This is a cross-tenant confusion vulnerability rooted in this gem's `shop` field not being part of the identity binding it participates in.

### Likelihood Explanation
Exploitation requires only an unprivileged internet user who can install the target app on any shop they control (a normal merchant action) to obtain one real signed webhook, then replay it with a modified `shop-domain` header to the app's public webhook endpoint. No access to `api_secret_key`, tokens, or privileged accounts is required.

### Recommendation
Bind the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) into the HMAC-verified signable material, or otherwise cryptographically tie the `shop-domain` header to the signed body (e.g., include it in the signed payload construction) before trusting `request.shop` for tenant attribution in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`; Shopify sends a legitimately signed webhook: body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` and succeeds.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to act on victim-shop's behalf using attacker-controlled body content.

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
