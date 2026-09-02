I found a clear identity-binding break in the webhook processing path.

### Title
`shop-domain` and `topic` headers used by webhook handlers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches to the app's handler using the `shop-domain`, `topic`, `api-version`, and `webhook-id` values taken from unauthenticated HTTP headers. These header values are never part of the signed content, so an attacker who can produce (or replay) a payload with a valid body/HMAC pair for one shop can freely swap the `shop-domain`/`topic` headers to make the host app process the event as if it came from a different, arbitrary tenant.

### Finding Description
`Webhooks::Request#hmac` and `#to_signable_string` derive the signature exclusively from `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only the body HMAC and then trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app-registered handler: [3](#0-2) 

The identity binding that should hold is: `hmac == HMAC(secret, raw_body || shop || topic)`, i.e. the tenant identifier acted upon (`shop`) must be covered by the same signature that authenticates the payload. Instead the code only proves `hmac == HMAC(secret, raw_body)`, while `shop` is parsed from an independent, unauthenticated header. Any request bearing a raw body whose HMAC is valid (e.g., a legitimately-signed webhook payload for the attacker's own connected shop, or a replayed payload the attacker captured) can be resubmitted with a different `x-shopify-shop-domain` (and/or `x-shopify-topic`) header, and the gem will invoke the handler believing the event originated from that other shop.

### Impact Explanation
This breaks the tenant boundary: an unprivileged actor who controls one legitimately webhook-registered shop (or who captures/replays a valid signed payload) can cause the host application's webhook handler to execute with attacker-chosen `shop` and `topic` values, misattributing data to another merchant's tenant. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up per-tenant records, credentials, or trigger tenant-scoped side effects), this enables cross-tenant data corruption or disclosure — satisfying the "cross-tenant access" Critical impact category, since the shop identity used for authorization/dispatch is not actually authenticated.

### Likelihood Explanation
Likelihood is moderate: the attacker needs at least one valid `(raw_body, hmac)` pair, which is achievable by any developer/merchant who has legitimately received a webhook for their own shop (or who can trigger one, e.g. via `shop/redact` or any subscribed topic) since `api_secret_key` is not required — only a previously observed valid signed body is needed, and the header can then be freely altered on replay to a different shop domain.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the value that is signed/verified (or otherwise cryptographically bind them to the body), or independently verify that the `shop-domain` header matches a shop known to be associated with the api_secret_key/app installation before dispatching to handlers. At minimum, treat `shop` and `topic` as attacker-controlled input unless bound into the HMAC computation.

### Proof of Concept
1. App has valid webhook registered; attacker (a merchant on shop A, or anyone who intercepts a webhook delivery) captures a legitimate webhook request: raw body `B`, header `x-shopify-hmac-sha256: H` (valid for `B`), `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker resends the exact same body `B` and `hmac` header `H` to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `shop-b.myshopify.com` (a victim tenant).
3. `Utils::HmacValidator.validate(request)` in `Registry.process` recomputes the HMAC only over `@raw_body`, which still matches `H`, so validation passes: [4](#0-3) 
4. `handler.handle` is invoked with `shop: request.shop` equal to `"shop-b.myshopify.com"`, even though the payload/HMAC never had any relationship to shop B: [5](#0-4)

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
