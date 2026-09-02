Based on my research, I found a clear analog to the reentrancy pattern's underlying bug class — an "acted-upon field not covered by the integrity check."

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` value that the gem hands to the app's handler is taken from an HTTP header that is never included in the signed material. Any party who can obtain one validly-signed webhook delivery (e.g., a merchant/attacker who installs the app on their own store) can replay that exact signed body while substituting the `shop-domain` header for a victim shop, and the gem will accept it as authentic.

### Finding Description
`Utils::HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string`, and for webhooks that is defined as just the raw body: [1](#0-0) 

The `shop` accessor, by contrast, is read straight from an unauthenticated header (`shopify-shop-domain` / `x-shopify-shop-domain`), with no cryptographic binding to the body or to the signature at all: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler — there is no check binding the header-derived `shop` to anything covered by the signature: [3](#0-2) 

The equality that should hold is:
`shop value cryptographically bound by HMAC == shop value delivered to the app's tenant-scoped handler`

In this implementation that equality does not hold: the HMAC only binds `raw_body`, while `shop` is an independent, attacker-controllable header field on any request that otherwise carries a genuinely valid signature (e.g., for the attacker's own store, since the HMAC secret — the app's `client_secret` — is shared across all shops using the app, not per-shop). An attacker who installs the target app on their own Shopify store receives real, validly-HMAC-signed webhook deliveries for their own shop. They can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while changing only the `shop-domain` header to a victim shop's domain. `HmacValidator.validate` still passes (it never looked at the header), and the app receives `WebhookMetadata` claiming the payload originated from the victim shop, per the documented handler contract: [4](#0-3) 

Per the gem's own documentation, apps are expected to use `data.shop` to route/persist data per-tenant (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), so this un-bound field is exactly the value host apps rely on to know which tenant a webhook belongs to.


### Impact Explanation
This breaks the tenant isolation the HMAC check is supposed to guarantee: an unprivileged internet user (any merchant who can install the app on their own shop) can make the gem/host app attribute attacker-controlled webhook data to an arbitrary victim shop. Depending on how the host app uses `data.shop` (e.g., to update per-shop records, trigger per-shop side effects, or index credentials), this is a cross-tenant data injection primitive, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker be an app user on their own shop (standard, unprivileged access to any public embedded app) and be able to send an HTTP POST with attacker-chosen headers to the app's webhook endpoint — no access to `api_secret_key`, tokens, or victim credentials is needed. Likelihood is moderate: it requires knowledge that this gem doesn't bind the shop header to the signature, but no privileged access.

### Recommendation
Include the `shop-domain` header (and ideally the topic/api-version headers) as part of the signed/verified material in `Utils::HmacValidator`/`Webhooks::Request`, or otherwise cryptographically bind the shop identity to the HMAC-covered payload before constructing `WebhookMetadata`. At minimum, document that `data.shop` is unauthenticated and must not be trusted for tenant routing without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers/receives a genuine webhook delivery from Shopify: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared `api_secret_key`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` computes the HMAC over `B` only [1](#0-0)  and it matches `H`, so validation succeeds.
5. `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` [5](#0-4)  and invokes the host app's handler, which believes the (attacker-controlled) payload `B` genuinely originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
