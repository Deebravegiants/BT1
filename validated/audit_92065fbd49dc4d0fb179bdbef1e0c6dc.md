Confirmed root cause: the webhook HMAC in this gem binds only the raw JSON body, while `topic`, `shop`, `webhook_id`, and `api_version` — the fields the handler actually acts on — are read straight from unauthenticated headers.### Title
Webhook `shop`, `topic`, and `webhook_id` are not bound to the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body alone, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates only the body's HMAC and then forwards these unauthenticated header values to the app's handler as the tenant identifier, breaking the binding between "the bytes Shopify signed" and "the shop the app acts on."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from `@headers` and never enter the signed string: [2](#0-1) 

`Registry.process` validates the HMAC (`Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string`/`request.hmac`) and then builds a `WebhookMetadata` struct straight from the same unauthenticated header accessors: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no further validation, and it is this value the host application's handler receives to decide which tenant record to update: [4](#0-3) 

The identity binding that should hold is:
`hmac_valid(body) == true` should imply `shop_header == shop_that_Shopify_actually_sent_this_body_for`.

In this implementation, `hmac_valid(body)` only proves the body bytes were signed with `api_secret_key` by Shopify for *some* delivery — it says nothing about which shop or topic that delivery was for. Because `shop-domain`, `topic`, and `webhook-id` sit outside the signed content, any party who possesses one valid `(body, hmac)` pair — for example a merchant who has installed the app on their own store and can inspect the legitimate webhook their own shop received — can resubmit the same body/HMAC pair to the app's webhook endpoint with a different `X-Shopify-Shop-Domain` header (and/or different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`). `HmacValidator.validate` will still pass because it only recomputes HMAC over `@raw_body`, and the handler will process the request as if it originated from the attacker-chosen shop.

This is exploitable without any credential belonging to the victim shop: the attacker only needs a legitimate account with the app on any shop of their choosing (an "unprivileged internet user" with respect to the target shop) plus generic HTTP access to the app's public webhook endpoint.

### Impact Explanation
This breaks tenant isolation (cross-tenant access), one of the explicitly in-scope Critical impacts. Any app built on this gem that trusts `WebhookMetadata#shop` (as documented/intended usage — see `docs/usage/webhooks.md`) to select which shop's records to mutate can have another shop's data corrupted, deleted, or exposed as a result of a replayed/relabeled webhook body. The severity depends on the topic (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`) but the underlying mechanism is a straightforward authentication/binding bypass at the library layer used identically by every consuming app.

### Likelihood Explanation
Likelihood is realistic: the attacker needs no secret material, no privileged account on the victim shop, and no TLS interception — only (1) a legitimate webhook delivery to a shop they control (or any shop, since bodies for certain topics can be predictable/minimal, e.g., `{}` or fixed-shape payloads), and (2) the ability to POST arbitrary headers/body to the app's public webhook callback URL, which is by design internet-reachable. The gem does nothing to prevent replay to a different logical shop because the shop identity is carried entirely outside the cryptographic envelope.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` (not just the raw body) in the HMAC-signed material, or otherwise cryptographically bind them (e.g., HMAC over `headers + body` canonicalized, mirroring how `AuthQuery#to_signable_string` binds `code/host/shop/state/timestamp` together in `lib/shopify_api/auth/oauth/auth_query.rb`). At minimum, `Registry.process` should not trust `request.shop`/`request.topic` unless they are covered by the same HMAC check that gates body integrity.

### Proof of Concept
1. App using this gem registers a webhook handler for topic `orders/create` (or any topic with a fixed/predictable minimal body, e.g. `{}`).
2. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker POSTs to the app's public webhook endpoint with the same body `B` and the same valid `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(secret, B) == H` (`lib/shopify_api/utils/hmac_validator.rb` lines 26-31, `lib/shopify_api/webhooks/request.rb` lines 35-38).
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb` lines 188-200), causing the app to act on the victim tenant using attacker-supplied context.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
