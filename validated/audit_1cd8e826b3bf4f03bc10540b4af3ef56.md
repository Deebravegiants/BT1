This confirms the vulnerability: the webhook HMAC (`to_signable_string` in `lib/shopify_api/webhooks/request.rb:35-38`) is computed only over `@raw_body`, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:15-33`) and passed straight through to the app's handler by `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) without any binding check between the signed body and the claimed shop/topic.

### Title
Webhook `shop`/`topic` identity is not bound by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` verifies the `X-Shopify-Hmac-Sha256` header against that raw body alone. The `shop-domain`, `topic`, and `webhook-id` values are taken verbatim from HTTP headers that are never included in the HMAC-signed material, yet `Registry.process` trusts and forwards them unchanged to the host application's webhook handler as the source of tenant identity.

### Finding Description
`Request#hmac`/`to_signable_string` bind only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read from headers that carry no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then dispatches using the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

Because every shop that installs the app shares the same app-level `client_secret` (`api_secret_key`) used to compute this HMAC, a body+HMAC pair that is genuinely valid for one tenant is *also* a valid HMAC for that exact body when submitted to the webhook endpoint with a different `shop-domain` header. The equality the code implicitly assumes — "HMAC verified" == "shop/topic headers are authentic" — does not hold, because the HMAC only proves "this body was signed by our app's secret," not "this body originated from, or concerns, the shop named in this header."

### Impact Explanation
An attacker who legitimately installs the target app on their own (attacker-controlled) shop will receive real webhooks with a valid HMAC computed over a body they fully control the shape of (since they control their own shop's data, e.g., product/order content). They can replay that exact `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting the `shop-domain` header of a victim tenant (and/or a different `topic` header, since `topic` is likewise unauthenticated). Because `Registry.process` only checks `Utils::HmacValidator.validate(request)` and never cross-checks that the shop/topic in the headers are consistent with anything bound into the signed payload, the handler receives `WebhookMetadata` claiming to belong to the victim shop with attacker-crafted body content. Any host application that uses `data.shop` from the handler to look up records, key a job queue, or otherwise scope writes/reads per tenant (exactly as shown in this gem's own documented example, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be made to attribute or apply attacker-controlled data to a different tenant — a cross-tenant boundary break.

### Likelihood Explanation
Requires only an unprivileged actor able to install the target app on a shop they control (a normal, low-privilege action for any public/embedded Shopify app) and the ability to send a raw HTTP POST to the app's public webhook endpoint — no access to the app's `client_secret`, access tokens, or victim credentials is needed.

### Recommendation
Bind tenant identity into the verified material: include the `shop-domain` (and ideally `topic`/`webhook-id`) in the HMAC-signable string, or independently verify that the `shop` header corresponds to a shop the app has an active installation/session for before dispatching to the handler, rather than trusting the header purely on the strength of a body-only HMAC.

### Proof of Concept
1. Install the target Shopify app on attacker-owned shop `attacker.myshopify.com`.
2. Trigger a webhook (e.g., `orders/create`) so Shopify sends a genuine POST with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Capture `B` and `H`.
4. Send a forged POST to the app's webhook endpoint reusing body `B` and header `X-Shopify-Hmac-Sha256: H`, but replace `X-Shopify-Shop-Domain` with `victim.myshopify.com` (and optionally change `X-Shopify-Topic`).
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only and finds it matches `H`, so validation passes.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)`, letting attacker-controlled content be processed as if it belongs to the victim tenant.

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
