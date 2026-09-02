### Title
Webhook `shop` and `topic` identity fields are trusted from unauthenticated HTTP headers while only the raw body is HMAC-covered - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` domain and the `topic` from HTTP headers, but the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator.validate` only covers the raw request body (`to_signable_string` returns `@raw_body`). This breaks the identity binding: `bytes verified (raw_body) != bytes that determine tenant/topic (headers)`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook request purely by checking the HMAC of the raw body: [1](#0-0) 

The HMAC is computed only over `@raw_body`: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` — all of which are read straight from HTTP headers, not the signed payload — are then trusted to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) [5](#0-4) 

Because the app's `client_secret` (used to sign webhooks) is the same for every shop that installs the app, and only the body bytes are authenticated, anyone who can obtain one valid `(raw_body, hmac)` pair for the app (e.g. by installing the app on their own shop and capturing a legitimate webhook delivery) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` will still return `true`, since it never inspects the `shop` header, and the handler will be invoked with `WebhookMetadata#shop` set to the attacker-chosen value — impersonating a webhook that appears to originate from a different (victim) shop.

Equality that should hold but doesn't: `shop authenticated by HMAC == shop passed to the handler`. In this design it's actually `shop passed to the handler == shop header value (unauthenticated)`.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker (any unprivileged Shopify merchant who has installed the target app) can forge webhook deliveries that the host application will process as if they came from a different shop, without needing that shop's credentials. Any host application that uses `WebhookMetadata#shop` to look up/update per-tenant records (as the documented usage pattern in `docs/usage/webhooks.md` explicitly recommends: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) is exposed to cross-tenant data corruption or disclosure driven entirely by this gem's trust model for the `shop` field.

### Likelihood Explanation
Moderate-to-high: exploitation requires the attacker to obtain at least one valid `(raw_body, hmac)` pair, which is trivial — they can install the app on their own store (a normal, unprivileged action) and capture any webhook delivery Shopify sends them, since the app's `client_secret` is shared across all shops. No access to the app's `client_secret`, no privileged account, and no TLS interception is required — only a plain HTTP replay to the app's own publicly reachable webhook endpoint with a modified header.

### Recommendation
Include the shop domain, topic, and API version in the HMAC-signed content (`to_signable_string`) rather than trusting them from unauthenticated headers, or otherwise cryptographically bind the header values to the signed payload before using them to identify the tenant in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Shopify delivers a legitimate webhook (e.g. `orders/create`) to the app's endpoint with headers including `X-Shopify-Hmac-Sha256: <valid-hmac>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and some raw body `B`.
3. Attacker captures `(B, valid-hmac)`.
4. Attacker sends a new POST request to the same webhook endpoint with the same raw body `B` and the same `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`= B`) only — it matches, so validation succeeds.
6. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
