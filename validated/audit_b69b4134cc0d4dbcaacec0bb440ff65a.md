This confirms the finding. The docs at `docs/usage/webhooks.md:125` explicitly state that `Registry.process` "will verify the request did indeed come from Shopify," and the `WebhookHandler` example at `docs/usage/webhooks.md:24-26` shows `data.shop` being trusted directly for tenant-scoped work (`shop_domain: data.shop`) — confirming that the gem's documented contract is for `shop` to be an authenticated field once `process` succeeds, while in fact only the raw body is HMAC-covered.

### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are trusted without HMAC coverage, breaking the shop-identity binding relied on by `Registry.process` - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` authenticates nothing but the body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from HTTP headers and are never included in the signed payload, yet `Webhooks::Registry.process` treats a successful HMAC check as proof the whole request — including these header-derived fields — "did indeed come from Shopify" (per `docs/usage/webhooks.md:125`) and hands them to the app's handler as trusted identity data.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

Only `@raw_body` is signed. `shop`, `topic`, `webhook_id`, and `api_version` are parsed from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build `WebhookMetadata`, passing them straight to the app's handler: [3](#0-2) 

The `VerifiableQuery` interface only requires `hmac` and `to_signable_string` — it provides no mechanism to bind auxiliary fields like `shop` into the signature: [4](#0-3) 

This is an equality that the gem implicitly claims holds but does not enforce:
`bytes verified by HMAC == identity fields (shop/topic/webhook_id) acted upon by the handler`.
In reality, `bytes verified` is strictly `raw_body`, while `shop` etc. are attacker-controllable header values whenever the attacker can produce *any* validly-signed body+HMAC pair for the shared `api_secret_key` (e.g., a legitimate webhook delivery to their own installed shop). The `shop-domain` header on that same request can be freely altered before it reaches the app's webhook endpoint, and `Registry.process` will still accept it, because the signature check never looks at headers.

### Impact Explanation
Because `api_secret_key` (and thus the HMAC) is shared across every shop that installs the app, a party who legitimately receives one authentic webhook delivery (i.e., who has installed the app on their own shop) can present that same authentic `body + hmac` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and `topic`/`webhook-id`) header. `HmacValidator.validate` still returns `true`, and `Registry.process` calls the app's handler with `WebhookMetadata#shop` set to the forged victim shop. Any host application that follows the documented pattern of using `data.shop` to route/persist webhook data per-tenant (as shown in the gem's own `docs/usage/webhooks.md` example, `shop_domain: data.shop`) will process or store data against the wrong tenant — a cross-tenant data integrity break stemming directly from an identity binding the gem does not actually enforce despite advertising verification of "the request."

### Likelihood Explanation
Requires no possession of `api_secret_key`, no TLS interception, and no privileged account — only the ability to install the app on any shop (an "unprivileged internet user" action available to anyone who can install a public/unlisted Shopify app) and then replay/re-POST a genuine webhook body+signature to the app's public webhook endpoint with a modified shop header. This is a straightforward header substitution using entirely legitimate, self-obtained signed material.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the value that is actually verified — e.g., require the host app to cross-check `request.shop` against the shop associated with `webhook_id`/topic registration via a server-side lookup, or extend `to_signable_string`/`VerifiableQuery` so that header-derived identity fields are covered by (or independently validated against) the HMAC, and update `docs/usage/webhooks.md` to stop asserting that a successful `process` call authenticates anything beyond the raw body.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a real webhook delivery: Shopify POSTs `raw_body` B with header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com` to the app's public webhook endpoint.
2. Attacker captures this exact `(B, HMAC)` pair (they are the intended final recipient of this specific delivery, so no interception is required).
3. Attacker re-sends an HTTP POST to the same webhook endpoint with body `B`, the same `x-shopify-hmac-sha256` header, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:13-22` succeeds because it only checks `B` against the HMAC.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host app (per the gem's documented pattern) processes/persists the forged payload under the victim shop's tenant record.

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L1-18)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Utils
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
  end
end
```
