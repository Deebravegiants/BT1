Based on the webhook processing code, there's a genuine identity-binding gap: the webhook HMAC signature only covers the raw request body, while the shop, topic, and webhook_id used by the application are taken from unsigned HTTP headers.

### Title
Webhook shop/topic/webhook_id are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable signable string from only the raw request body, while `shop`, `topic`, and `webhook_id` are parsed from HTTP headers that are never included in the HMAC computation. `Registry.process` validates the HMAC and then dispatches to the app's handler using these unauthenticated header values, so any actor able to obtain one validly-signed webhook body/HMAC pair (e.g. a merchant who installs the app on their own shop and receives genuine webhooks) can replay that same body+HMAC with a different `shop-domain`/`topic`/`webhook-id` header set, and the library will accept it as authentic for the spoofed shop/topic.

### Finding Description
`Request#hmac` reads the `hmac-sha256` header and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

Meanwhile `shop`, `topic`, and `webhook_id` are read straight from headers with no cryptographic binding to the signature: [3](#0-2) 

`Registry.process` validates the HMAC over the body via `Utils::HmacValidator.validate(request)`, and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` (all header-derived, unsigned) to build the `WebhookMetadata` handed to the application's handler: [4](#0-3) 

The HMAC secret (`Context.api_secret_key`) is the app's single client secret, shared across every shop that installs the app — it is not shop-specific. This means any merchant who installs the app receives genuine Shopify-signed webhook bodies for their own shop. Because the signature only commits to the body bytes, that same signed body can be replayed to the endpoint with the `shop-domain` (and/or `topic`, `webhook-id`) header rewritten to name a different, victim shop. `HmacValidator.validate` will still succeed since it only re-derives the signature from `@raw_body`, so `Registry.process` will treat the forged request as an authentic webhook for the victim shop.

This breaks the identity binding: **the shop authenticated by the HMAC (i.e. "some shop signed by this app secret") ≠ the shop the handler is told the event belongs to (`request.shop` from the header)**.

### Impact Explanation
This allows cross-tenant confusion: an attacker with a legitimately-installed instance of the app can generate arbitrary genuine (body, hmac) pairs (by triggering events on their own store) and replay them against the shared webhook endpoint while claiming they originate from any other shop. Depending on how the app's `handler.handle` logic uses `WebhookMetadata#shop` (e.g., to look up/modify per-tenant data, mark orders paid, cancel subscriptions, etc. for the named shop), this can lead to unauthorized cross-tenant data manipulation — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Requires the attacker to control at least one shop/app installation that can receive genuine webhooks (a low bar — installing a public app is unprivileged), and requires the app's business logic to trust `WebhookMetadata#shop` as a tenant key without additional cross-checks (a very common pattern, as shown in the gem's own docs which pass `data.shop` directly to app logic).

### Recommendation
Include `shop`, `topic`, and `webhook_id` header values in the HMAC-signed payload (or otherwise cryptographically bind them, e.g., by having `to_signable_string` incorporate the full raw request including these headers, consistent with how Shopify signs the payload), or explicitly document/require callers to cross-check `data.shop` against an expected/registered shop list rather than trusting the header value implicitly once HMAC on the body succeeds.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/paid`, with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and raw JSON body `B`.
2. Attacker resends the exact same body `B` and same `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim.myshopify.com` (and/or changes topic/webhook-id headers).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` — validation succeeds because the body and secret are unchanged.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the app processes the forged event as if it were legitimately sent by Shopify for the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
