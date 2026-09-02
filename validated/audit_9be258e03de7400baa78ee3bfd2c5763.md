### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, and `webhook_id` are read from unauthenticated HTTP headers. `Registry.process` accepts the request as long as the HMAC over the body matches, then forwards the header-derived `shop` value straight to the app's handler as the tenant identifier, without that value ever being covered by the signature.

### Finding Description
`HmacValidator.validate` verifies a `VerifiableQuery`'s HMAC against `to_signable_string`. [1](#0-0) 
For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 
Meanwhile `shop`, `topic`, and `webhook_id` are pulled directly from HTTP headers with no cryptographic binding to that signature: [3](#0-2) 
`Registry.process` validates only the body HMAC and then hands the header-derived, unauthenticated `shop` value straight to the application's webhook handler as the tenant key: [4](#0-3) 

This is the same bug class as the report: a value that is *acted upon* (here, the `shop` tenant identifier used by the handler to look up/mutate per-shop data) is not covered by the verification that is supposed to authenticate the message (here, the HMAC only covers `raw_body`). The equality that should hold — "the shop the HMAC authenticates" == "the shop the handler trusts" — is broken, because the HMAC authenticates zero bytes of the `shop` field.

Because the app's `api_secret_key` is shared across every shop that installs the app, any unprivileged user who installs the app on their own shop can capture a legitimately-signed `(raw_body, hmac)` pair from a webhook delivered to their own endpoint. They can then replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `Registry.process` will validate the HMAC (it only checks body bytes) and dispatch the event to the handler claiming to be from the victim shop.

### Impact Explanation
This crosses the tenant boundary: an attacker who has legitimate but unprivileged access to the app (their own store install) can forge webhook events attributed to a different, victim shop. Depending on how the host application's webhook handler uses `WebhookMetadata#shop` (e.g., to update per-shop database records, trigger `app/uninstalled` cleanup, or process `orders/create`/`shop/update` payloads), this enables cross-tenant data corruption or spoofed business events for a shop the attacker does not control. This matches the "cross-tenant access" Critical impact category from the given scope.

### Likelihood Explanation
Medium: it requires the attacker to (a) install the app on a shop they control to obtain a valid `(body, hmac)` pair, and (b) know or guess the victim's `myshopify.com` domain (easily discoverable, e.g., via the app's own install records or public storefront). No secret key or privileged access is required — this is achievable by any unprivileged internet user who can install the app once, which is the same class of trust exploited by the reported Stargate/Tapioca bug (an unchecked/miscomputed binding that lets bytes "verified" diverge from bytes "acted on").

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string bound to the HMAC, or otherwise cryptographically bind these header values to the request before trusting them, e.g.:

```diff
 sig { override.returns(String) }
 def to_signable_string
-  @raw_body
+  "#{topic}|#{shop}|#{webhook_id}|#{@raw_body}"
 end
```

Note: Shopify's actual HMAC computation over webhook deliveries is fixed to the raw body only (server-side), so a compatible fix would instead require documenting that `shop`/`topic`/`webhook_id` are *not* authenticated by `HmacValidator.validate`, and instructing consuming applications to independently verify that the `shop` in the payload/header corresponds to a shop with an active, stored session before acting on the webhook (i.e., look up the session for that shop and reject webhooks for shops without an installed session, rather than trusting the header blindly).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays an HTTP POST to the same app webhook endpoint with:
   - Body: `B` (unchanged)
   - Header: `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since HMAC only covers `B`)
   - Header: `X-Shopify-Shop-Domain: victim.myshopify.com` (attacker-controlled)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only returns `@raw_body`. [4](#0-3) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` and processes the event as if it legitimately originated from `victim.myshopify.com`, even though the victim never sent it.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
