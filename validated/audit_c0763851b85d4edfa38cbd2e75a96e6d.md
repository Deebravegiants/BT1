### Title
Webhook `shop` identity is derived from an unauthenticated header, unbound to the HMAC over the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw request body, then forwards a `shop` value taken from the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header — a field never included in the HMAC computation — to the host application's handler as trusted tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers, none of which participate in the signable string: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)`, then immediately builds `WebhookMetadata` using `request.shop` (and the other header-derived fields) and passes it to the app's registered handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no cryptographic binding to the authenticated payload: [4](#0-3) 

The identity binding the gem should enforce is: `shop-domain header == tenant that produced the HMAC-signed body`. In reality the gem enforces only `HMAC(secret, body) == received_signature`; the `shop` (and `topic`/`webhook_id`) values are copied verbatim from unauthenticated headers with no check that they correspond to the entity that actually generated the signed body. Any unprivileged internet user who operates their own legitimate Shopify store can trigger a real webhook for their own shop (a valid `hmac-sha256` over a real `raw_body`, signed with the app's shared secret, which Shopify sends to the merchant's own store just the same), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` passes the forged `shop` string straight to the handler as if it were authenticated.

### Impact Explanation
Applications built on this gem (and its companion `shopify_app`) commonly key session/tenant lookup, database routing, or authorization decisions off `WebhookMetadata#shop`. Because that field is not bound to the HMAC-verified body, an attacker who owns any store on the platform can forge webhook deliveries that claim to originate from a victim shop, or make it appear that an app-uninstall/order-cancel/GDPR-style webhook came from a shop it did not come from. This crosses the tenant boundary the HMAC check was supposed to guarantee — matching the Critical "cross-tenant access" category, since the app is misled into acting on data for the wrong merchant.

### Likelihood Explanation
No credential, token, or leaked secret is required beyond having any working store to receive one legitimate signed webhook. Only header manipulation on a replayed HTTP request is needed, which is trivially available to any internet user with an account capable of triggering webhooks (e.g., a free development store). The gem provides no additional check tying `shop` to the signed content, so the attack surface is always present wherever `Registry.process`/`WebhookMetadata#shop` is used by the host app.

### Recommendation
Include the tenant-identifying fields (`shop-domain`, and ideally `topic`/`webhook_id`) inside the HMAC-signed material, or otherwise cryptographically bind them to the verified payload before they are exposed via `WebhookMetadata`. At minimum, `Utils::HmacValidator.validate` should be extended (or a new check added) to fail closed unless the `shop` header value can be independently corroborated (e.g., against a known/allow-listed set of shops for the app, or by including it in the signable string as Shopify does for OAuth `AuthQuery`, which does cover `shop` in its `to_signable_string`) — see `lib/shopify_api/auth/oauth/auth_query.rb`'s `to_signable_string`, which correctly folds `shop` into the signed data, as a model to follow for webhooks.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com`, a legitimate store with the target app installed, and receives a real webhook delivery:
   - Headers: `X-Shopify-Topic: app/uninstalled`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - Body: `{"...": "..."}` (untouched, so the HMAC stays valid)
2. Attacker resends the identical body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (headers present), `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only checks `@raw_body`, which is unchanged: [5](#0-4) 
4. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host application processes/records an action as if it genuinely originated from `victim-shop.myshopify.com`: [3](#0-2)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
