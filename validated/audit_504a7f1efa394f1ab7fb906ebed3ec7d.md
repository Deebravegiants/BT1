This confirms the finding. In OAuth (`AuthQuery#to_signable_string`), the `shop` field IS included in the signed string, so the HMAC binds the shop identity. But for webhooks (`Webhooks::Request#to_signable_string`), only `@raw_body` is signed — the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are excluded from the HMAC computation, yet `Registry.process` trusts `request.shop` when constructing `WebhookMetadata` passed to the app's handler.

### Title
Webhook shop-domain header is trusted without HMAC binding, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers via `shopify_header`. `Registry.process` validates the HMAC over the body only, then forwards the unauthenticated `shop` value straight to the app's `WebhookHandler`. Because Shopify signs webhooks with the app-wide `client_secret` (shared across every shop that has the app installed), any actor who legitimately receives a webhook for one shop they control can replay that same body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header, and the gem will accept it as authentic for the spoofed shop.

### Finding Description
`HmacValidator.validate` calls `verifiable_query.to_signable_string` to compute the expected signature [1](#0-0) . For webhooks, `to_signable_string` returns `@raw_body` exclusively [2](#0-1) , whereas `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from HTTP headers with no cryptographic binding [3](#0-2) .

`Registry.process` only re-validates the HMAC (over the body) before dispatching to the handler with the unauthenticated `request.shop` value: [4](#0-3) 

By contrast, the OAuth callback path binds `shop` into the signed content — `AuthQuery#to_signable_string` explicitly includes `shop` in the HMAC-covered parameters [5](#0-4) , so the equality "HMAC-verified shop == acted-upon shop" holds for OAuth but is broken for webhooks.

The binding that fails: `shop header value used by the handler` should equal `shop value covered by the HMAC`, but for webhooks the HMAC only covers `raw_body`, so any header value can be substituted post-signing without invalidating the HMAC.

### Impact Explanation
Shopify computes webhook HMACs using the app's single `client_secret`, which is shared across all shops that install the app — it is not shop-specific. An attacker who installs the app on their own shop (or otherwise legitimately receives a valid webhook payload+HMAC for a topic/body they control) can intercept that request and resend it to the app's webhook endpoint with the `shop-domain` header changed to a victim shop. Because `Registry.process` only checks the HMAC against `raw_body`, the forged request passes validation, and the handler receives `WebhookMetadata` claiming the data belongs to the victim shop [6](#0-5) . Applications that key off `data.shop` to look up sessions, update per-shop state, or trigger shop-scoped side effects (order creation, GDPR redact handling, etc.) can be tricked into attributing attacker-controlled data to a different tenant — a cross-tenant integrity violation reachable by any unprivileged actor who can install the app once.

### Likelihood Explanation
Requires only that the attacker be able to install the target app on a shop they control (a normal, unprivileged action for any Shopify merchant/developer) and be able to send an HTTP POST to the app's public webhook endpoint with a modified header — no access token, `client_secret`, or privileged account is needed.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-covered material for webhooks, or otherwise cryptographically bind the shop-domain header to the signed payload before `Registry.process` trusts it, mirroring the approach already used in `AuthQuery#to_signable_string`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the request: body `B`, and header `x-shopify-hmac-sha256` = HMAC(`client_secret`, `B`).
2. Replay the captured request to the app's webhook endpoint, keeping body `B` and the HMAC header unchanged, but replacing `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`= B`) and matches the unmodified header — validation succeeds [7](#0-6) .
4. The registered handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` now returns `"victim.myshopify.com"` [6](#0-5) , causing the host application to process attacker-controlled data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
