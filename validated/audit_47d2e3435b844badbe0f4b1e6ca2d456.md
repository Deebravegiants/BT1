This confirms the finding: `to_signable_string` in `lib/shopify_api/webhooks/request.rb` line 36-38 returns only `@raw_body`, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers and never included in the HMAC-signed string.I have sufficient evidence to finalize the analog finding.

### Title
Webhook Shop-Domain and Topic Headers Are Not Bound by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The Cally fee-token bug is a class of "unbound field" problem: a value that the contract *acts on* (transferred token amount) is never checked for equality against the value that was *actually verified* (amount sent). The same class of defect exists in this gem's webhook processing: the `shop` and `topic` values that `ShopifyAPI::Webhooks::Registry.process` uses to route and attribute an incoming webhook are read from unauthenticated HTTP headers, while the HMAC signature that proves authenticity only covers the raw request body.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are all read directly out of caller-supplied HTTP headers with no cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then unconditionally trusts `request.shop` and `request.topic` to dispatch the webhook to the registered handler and to build the metadata object the host application acts on: [3](#0-2) 

This breaks the intended identity binding: `HMAC-verified(bytes) == bytes-acted-on`. In this gem, all shops installed on the same app share a single `client_secret`/`api_secret_key`, so the HMAC by itself only proves "some webhook legitimately originated from Shopify for this app" — it does **not** prove "for shop X". The `shop-domain` header is the *only* signal binding a webhook payload to a specific tenant, and it is exactly the field excluded from the signed bytes.

### Impact Explanation
An attacker who has legitimately installed the app on their own store (a real, low-privilege, non-victim tenant) receives genuinely HMAC-signed webhooks from Shopify for their own shop. Because the signature covers only the body and not the `shop-domain`/`topic` headers, the attacker can replay that same valid `(body, hmac)` pair to the host application's webhook endpoint while substituting `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) with an arbitrary victim shop domain and/or topic. `Utils::HmacValidator.validate` still succeeds because it only recomputes the signature over `@raw_body`, and `Registry.process` will hand the forged `WebhookMetadata` (with the attacker-chosen `shop`) to the app's registered handler as if it were data belonging to the victim shop. Any host application logic that trusts `data.shop` from this gem (e.g., looking up the victim's stored session/access token to react to the "webhook") is now operating on attacker-controlled shop attribution — a cross-tenant confusion primitive.

### Likelihood Explanation
The prerequisite (installing the target app on an attacker-controlled shop to obtain a validly signed webhook body) is achievable by any ordinary merchant/unprivileged internet user for any publicly installable app, and does not require the `api_secret_key`, an access token, or any privileged access. Replaying a captured HTTP request with modified headers is trivial.

### Recommendation
Include the authenticated identity fields (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the verified body (e.g., signing `"#{shop}|#{topic}|#{raw_body}"`) so `to_signable_string` cannot be satisfied while the shop/topic headers are forged independently of the signed payload.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and triggers/receives a real webhook (e.g., `orders/create`), capturing the raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (`H = HMAC-SHA256(api_secret_key, B)`).
2. Attacker POSTs `B` with header `H` unchanged to the host app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and, if desired, a different `X-Shopify-Topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`== B`) and matches `H`, so validation passes: [4](#0-3) 
4. `Registry.process` dispatches to the handler with `shop: request.shop` set to `victim-shop.myshopify.com`, even though the signed bytes never proved anything about that shop: [5](#0-4)

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
