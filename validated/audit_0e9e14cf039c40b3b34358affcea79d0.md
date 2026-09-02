### Title
Webhook `shop-domain` and `topic` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop`, `topic`, and `webhook_id` values taken from HTTP headers that are never included in that signature, and hands them to the app's `WebhookHandler` as authenticated `WebhookMetadata`.

### Finding Description
`Utils::HmacValidator.validate(request)` computes the HMAC over `request.to_signable_string`, which for `Webhooks::Request` is defined as just the raw body: [1](#0-0) 
The `shop`, `topic`, `webhook_id`, and `api_version` accessors, however, are read straight from unauthenticated headers (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`): [2](#0-1) 
`Registry.process` validates only the HMAC and then forwards these header-derived values, unverified, into `WebhookMetadata` passed to the merchant app's handler: [3](#0-2) 
`WebhookMetadata.shop` is a plain `String` field with no cryptographic binding to the signed body: [4](#0-3) 

Because the HMAC is computed over the body only, the equality the library actually enforces is:
`HMAC(body, client_secret) == received_hmac`
but the identity binding the handler *believes* it received is:
`shop == data.shop` (i.e., "this body genuinely originated from `data.shop`")

These are not the same guarantee. A merchant who has legitimately installed the app on their own store (tenant A) receives genuine webhooks from Shopify with a valid HMAC computed over a body. Since the `x-shopify-shop-domain` (and `x-shopify-topic`) header is excluded from the signable string, tenant A can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting `x-shopify-shop-domain` with tenant B's domain. `HmacValidator.validate` still succeeds because it only checks the body's signature, and `Registry.process` passes the forged `shop` value straight through to the handler as if it were authenticated.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: an app relying on `WebhookMetadata#shop` (as the documented/only means of tenant attribution provided by this gem) to decide which merchant's data to read, write, or delete can be tricked into acting on tenant B's identity using a payload actually originating from tenant A. This is a cross-tenant access vector directly enabled by the gem's own request/verification design, not a host-app misuse — the gem markets `Registry.process` plus `Utils::HmacValidator.validate` as the complete verification story for webhooks.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate merchant installing the app once (very low bar — public apps accept installs from any store) and the ability to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint, which is normal internet-reachable infrastructure for every Shopify app using this gem.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (or otherwise cryptographically bind them to the body/signature) so that `Utils::HmacValidator.validate` fails if any of these identity-bearing headers are tampered with, rather than only covering the JSON payload.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, and triggers a real webhook (e.g., `orders/create`) — Shopify sends a POST with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's `client_secret`.
2. Attacker captures `raw_body` and the valid `hmac` header value.
3. Attacker resends the same request to the app's webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` unchanged but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` still validate successfully because `to_signable_string` only reflects `raw_body`: [1](#0-0) 
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, even though the payload never originated from that shop: [5](#0-4)

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
