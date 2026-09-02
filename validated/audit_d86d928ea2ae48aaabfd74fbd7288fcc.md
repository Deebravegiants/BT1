## Analysis Summary

The reachable analog of the "acted upon but not covered by the integrity check" bug class in `shopify-api-ruby` is the webhook `shop` domain identity binding in `lib/shopify_api/webhooks/`.

### Title
Webhook `shop` tenant identifier is not covered by the HMAC signature, allowing cross-tenant webhook confusion - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the raw request body via HMAC, but hands the caller-supplied `shop-domain` header to the handler unauthenticated. Any actor who can obtain one genuinely-signed webhook (trivial for any merchant/attacker who installs the app on their own store) can replay that exact body+HMAC pair while substituting an arbitrary `shop-domain` header, causing the app to process attacker-controlled payload data as if it belonged to a victim tenant.

### Finding Description
`HmacValidator.validate` computes and compares the HMAC only over `to_signable_string`, which for a webhook `Request` is simply the raw HTTP body: [1](#0-0) 

The `shop` accessor, however, is read directly from the `shopify-shop-domain` header, which is never included in the signable string and therefore never verified: [2](#0-1) 

`Registry.process` checks the HMAC and then immediately forwards `request.shop` to the handler as the tenant identifier, without any additional binding between the verified body and the claimed shop: [3](#0-2) 

The identity binding that should hold is:
`hmac_valid(body) == true` **should imply** `shop == the tenant that produced body`

but the code only proves `hmac_valid(body) == true`; it never proves `shop` is bound to that specific body. Contrast this with the OAuth callback path, where the equivalent `AuthQuery#to_signable_string` explicitly includes `shop` in the signed content, correctly binding shop to the signature: [4](#0-3) 

### Impact Explanation
An unprivileged attacker who has installed the target app on their own store (a routine, unprivileged action any developer can perform) will legitimately receive real webhooks — valid body + valid HMAC — for their own shop. Because the `shop-domain` header is outside the signed content, the attacker can resend that exact `(body, hmac)` pair to the app's webhook endpoint while swapping in a victim shop's domain in the `shopify-shop-domain` header. `Registry.process` will accept it (HMAC still validates against the untouched body) and invoke the registered handler with `WebhookMetadata#shop` set to the victim's domain and `body` set to attacker-controlled content.

Any handler that uses `shop` to scope tenant data or trigger tenant-specific side effects (e.g., updating stored order/inventory state, or the mandatory `shop/redact` / `customers/redact` compliance topics that operate using the victim's stored session/access token) will act on the victim tenant using attacker-supplied data. This is a cross-tenant access/data-integrity break attributable entirely to the gem's own trust boundary, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that allows self-installation (most public apps do): the attacker needs no secrets, tokens, or privileged access — only the ability to install the app on a shop they control and to trigger any webhook topic whose payload they can influence or predict, then replay it with a modified header at the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed material used for verification, or otherwise cryptographically bind the claimed shop to the verified body (e.g., include the shop header in `to_signable_string`, matching the pattern already used in `Auth::Oauth::AuthQuery`). At minimum, document and enforce that consuming applications must independently verify that `shop` corresponds to a shop with an active install before trusting webhook content for that tenant.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`.
2. Attacker triggers (or waits for) a webhook, e.g. `orders/create`, and captures the raw request: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker resends the exact same body `B` and header `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` computes `HmacValidator.validate(request)` over `B` only — it passes because `B` and `H` are untouched.
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)` and processes attacker-controlled `B` as if it originated from `victim.myshopify.com`. [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
