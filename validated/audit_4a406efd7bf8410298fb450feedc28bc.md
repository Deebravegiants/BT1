This confirms the vulnerability. The `shop` field (along with `topic`, `api_version`, `webhook_id`) is read directly from HTTP headers via `shopify_header` in `Webhooks::Request`, but `to_signable_string` only returns `@raw_body` — meaning the HMAC signature Shopify computes only covers the request body, never the `shop-domain` header. `Registry.process` trusts `request.shop` and passes it straight into `WebhookMetadata` for the handler to act on, with no cross-check against the body or any other authenticated field. [1](#0-0) [2](#0-1) 

### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from an unauthenticated HTTP header (`shopify-shop-domain`/`x-shopify-shop-domain`), while the HMAC signature verified by `HmacValidator` is computed only over the raw request body (`to_signable_string` returns `@raw_body`). This breaks the identity binding `shop header == HMAC-authenticated shop`, since the `shop` value used downstream by `Registry.process` is never part of the signed payload.

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the `VerifiableQuery` object. For `Webhooks::Request`, `to_signable_string` is hardcoded to just `@raw_body`:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are all read from HTTP headers via `shopify_header`, which are never included in the signed string:

```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
```

`Registry.process` validates the HMAC (which only proves the *body* bytes were signed by the app's shared secret at some point) and then unconditionally trusts `request.shop` for dispatching to the handler:

```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler = @registry[request.topic]&.handler
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```

The identity binding that should hold is: `shop field trusted by handler == shop that the HMAC-signed payload actually originated from`. Because the header carrying `shop` is outside the HMAC's coverage, this equality is not enforced by the gem. Any actor who can obtain one valid `(raw_body, hmac)` pair signed with the app's shared secret — for example a merchant who legitimately installed the app and received/can produce a webhook delivery for their *own* shop — can replay that exact body/hmac pair to the app's webhook endpoint while swapping only the `shopify-shop-domain` header to a victim shop's domain. The HMAC check still passes (it only checks the body), but `request.shop` now falsely claims to be the victim tenant, and the host application's `WebhookHandler` (which typically looks up the victim's session/data using `data.shop`) processes attacker-controlled body content under the victim shop's identity — a cross-tenant confusion inside this gem's own trust boundary (`Registry.process` → `WebhookMetadata`).

### Impact Explanation
This breaks tenant isolation: the gem hands the host application a `shop` value that is not bound to the payload's authenticity, enabling processing of a webhook body as if it belonged to a different merchant's shop. This matches the Critical "cross-tenant access" impact category, since the shop identity used by all downstream webhook handling logic is not actually authenticated by the HMAC that this gem itself verifies.

### Likelihood Explanation
Exploitation requires obtaining at least one legitimately-signed `(raw_body, hmac)` pair for the app (achievable by any merchant who installs the app and triggers/observes one webhook delivery for their own store, or via any body content whose exact bytes can be predicted/repeated, e.g. an empty or fixed-shape payload for a given topic), then re-sending that exact body/hmac to the app's public webhook endpoint with a forged `shop-domain` header. No `api_secret_key`, access token, or privileged account access is needed beyond what an ordinary app-installing merchant already has. This is a realistic, low-effort attack path once one valid webhook has been observed.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, and ideally `api_version`/`webhook_id`) in the HMAC-signed string, e.g. by concatenating them with the raw body before hashing, and reject the header comparison to the signed value on mismatch — mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` into its signable payload. At minimum, `Webhooks::Request#to_signable_string` should not silently omit `shop`/`topic` from what `HmacValidator` verifies.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) for their own shop, capturing the raw body and the `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker POSTs to the app's webhook endpoint with the exact same raw body and `hmac-sha256` header, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `@raw_body` against the HMAC — the forged `shop-domain` header is never checked. [2](#0-1) 
4. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"`, causing the host app's handler to process attacker-supplied webhook content under the victim's tenant identity. [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
