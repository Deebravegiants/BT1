Confirmed: the HMAC in `ShopifyAPI::Webhooks::Request` covers only the raw body via `to_signable_string` returning `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unsigned HTTP headers via `shopify_header`. [1](#0-0) [2](#0-1) [3](#0-2) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` (which signs/verifies `to_signable_string`, i.e. the body only) and then constructs `WebhookMetadata` using `request.shop` taken straight from the `shop-domain` header, with no cross-check that the header value is bound to the signed content.

### Title
Webhook `shop` (and topic/webhook-id) header is trusted without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC-SHA256 signature validated by `Utils::HmacValidator.validate` in `Registry.process` binds solely to the request body. The `shop-domain` header (exposed via `Request#shop`) and other Shopify headers are read independently and are not part of the signed material, so they are never proven to originate from Shopify for the given signature.

### Finding Description
`Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares to `verifiable_query.hmac`. For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body`; the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are excluded from the signed string. This breaks the equality that should hold: `shop authenticated by HMAC == shop acted upon by the handler`. Anyone who can obtain one valid `(raw_body, hmac)` pair — e.g., a user who installs the app on their own store and receives a legitimate webhook delivery for a topic whose payload doesn't self-identify the shop — can resend that same body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. The signature still validates (it only checks the body), but `WebhookMetadata#shop` now reports a shop the attacker doesn't control.

### Impact Explanation
This crosses the tenant boundary the rules call out ("a shop authenticated versus the shop stored as a session key"): the host app's webhook handler is told data belongs to shop B while only shop A's body/signature was actually verified. Depending on how the host app implements handlers (e.g., GDPR `customers/redact`, `shop/redact` mandatory topics, uninstall/app-subscription handling, or any handler that looks up/mutates per-shop state keyed by `data.shop`), this enables cross-tenant data confusion or forged lifecycle events attributed to a shop the attacker does not own.

### Likelihood Explanation
Webhook endpoints are unauthenticated internet-reachable POST endpoints by design (Shopify calls them without any session). Any external actor who can install the app on any shop (including a free/dev store) can capture a legitimate signed webhook body and HMAC pair for a topic where the body content doesn't uniquely bind the sending shop, then replay it against the same endpoint with a forged `shop-domain` header — no `api_secret_key` or credentials are needed for the header-substitution step since the signature check never inspects the header.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signed material, or otherwise independently verify that the header-provided shop is consistent with the shop identifiable from the verified body/webhook metadata before invoking handlers, e.g., signing over `"#{shop}\n#{topic}\n#{raw_body}"` or requiring handlers to fetch/validate the shop through a mechanism bound to the signature.

### Proof of Concept
1. Register an `Http` handler for topic `T` that trusts `data.shop` (e.g., stores/deletes tenant data keyed by shop).
2. Attacker installs the app on `attacker-shop.myshopify.com`, triggers topic `T`, and captures the legitimate request: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `HMAC(secret, B) == H`).
3. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` since it only recomputes `HMAC(secret, B)`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and invokes the handler, which now acts on `victim-shop` using attacker-controlled/forged conditions.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
