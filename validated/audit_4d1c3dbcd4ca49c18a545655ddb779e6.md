### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are taken directly from unauthenticated HTTP headers and passed to the merchant's webhook handler as if they were verified. Because `Utils::HmacValidator.validate` only proves that the *body* was produced with the app's shared secret — not that the accompanying `shop-domain` header belongs to the shop that actually triggered the webhook — an attacker who controls any shop with the app installed can replay a genuine `(body, hmac)` pair while substituting an arbitrary victim shop domain, breaking the binding `hmac == HMAC(secret, body)` from actually authenticating `shop`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers, none of which are covered by the HMAC: [2](#0-1) 

`Registry.process` validates only that the HMAC matches, then forwards the header-derived `shop` (and other header values) unchanged to the app's handler: [3](#0-2) 

The HMAC-secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that has the app installed — it is not per-shop. Because the signature covers only the body, any valid `(raw_body, hmac)` pair captured from a legitimate webhook to shop A remains valid when replayed with `x-shopify-shop-domain: shop-B.myshopify.com`. The identity binding that should hold — "the shop asserted in the request equals the shop that the HMAC-authenticated bytes originated from" — is not enforced anywhere in this gem's webhook path.

### Impact Explanation
This falls in the "field acted on but not covered by the HMAC" analog class explicitly called out for this scan. An attacker who legitimately installs the app on their own store (an unprivileged action, requiring no merchant/staff credentials or leaked secrets) can capture genuine `(body, hmac)` pairs from their own webhooks, then forge the `shop-domain` header to any other shop that also uses this app, and the gem will report the request as HMAC-valid and dispatch it to the handler as belonging to the victim shop. Any host application that uses `request.shop` from `WebhookMetadata` to key session/data lookups (which is the intended and documented use of `WebhookMetadata#shop`) can be tricked into attributing attacker-controlled webhook data to a different, victim tenant — a cross-tenant data-confusion / cross-tenant access primitive.

### Likelihood Explanation
Requires only application installation as an unprivileged merchant (no special access, no leaked credentials, no TLS interception), plus the ability to send a crafted HTTP request with modified headers to the app's webhook endpoint — well within reach of "unprivileged internet user" as scoped by this scan.

### Recommendation
Bind the asserted `shop` (and ideally `topic`/`webhook_id`) into the signable content, or otherwise require the host application to cross-check `request.shop` against a known/registered shop-to-session mapping before trusting it. At minimum, document loudly that `request.shop` is unauthenticated header data and must never be trusted as a tenant identifier without independent verification.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`. Shopify sends a real webhook: body `B`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`, valid `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker resends the same request to the app's webhook endpoint, keeping body `B` and the same HMAC, but replacing the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` (comparing `HMAC(secret, B)` against the unchanged signature) succeeds, since `to_signable_string` never included the shop header: [1](#0-0) 
4. `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` and body `B`, even though `B` never originated from `victim-shop`: [3](#0-2)

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
