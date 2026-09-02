### Title
Webhook shop-domain identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw body only, while the `shop` (tenant identity) is taken from an unsigned HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates only that HMAC and then forwards the header-derived `shop` value to the app's handler as the trusted tenant identifier, breaking the binding `HMAC(secret, signed_content) == HMAC(secret, body)` from `shop`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` alone: [1](#0-0) 
while `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the body or the HMAC: [2](#0-1) 

`Registry.process` validates only the body HMAC and then trusts the header-derived shop when constructing the metadata passed to the consuming app's handler: [3](#0-2) 

Critically, the webhook HMAC secret (`Context.api_secret_key`) is the app's single client secret shared across *every* merchant/shop that installs the app — it is not per-shop: [4](#0-3) 

Because the signature only binds `secret + body` and never binds `shop`, any unprivileged merchant who installs the app on their own store (a normal, unprivileged action for a public app) receives legitimately-signed webhook deliveries for topics/bodies they can influence (e.g. `app/uninstalled`, `orders/create`, `customers/data_request`, etc., with attacker-controlled content in the JSON body). The attacker can capture one such validly-signed `(body, hmac)` pair from their own shop and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will accept it (it never inspects `shop`), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim shop as the origin: [5](#0-4) 

This is precisely the "field acted on but not covered by the HMAC" identity-binding break: `shop` is trusted as the tenant key for downstream processing (e.g. looking up/updating per-shop state, honoring `app/uninstalled` to wipe a victim's data, or injecting attacker-controlled body content attributed to the victim), yet it never participates in the signature that authenticates the request as genuinely originating for that shop.

### Impact Explanation
This breaks the shop/tenant identity binding and allows cross-tenant forgery of webhook events: an attacker-controlled shop can produce a webhook payload that the app processes as if it came from an arbitrary victim shop. Depending on how the consuming app implements its webhook handlers (a pattern this gem's own webhook framework explicitly encourages via `WebhookMetadata#shop`), this can lead to cross-tenant data corruption, spoofed `app/uninstalled` cleanup against a victim, or injection of attacker-chosen data attributed to a victim shop — a cross-tenant access impact.

### Likelihood Explanation
Any entity able to install the public app on their own shop (an unprivileged, standard action, not requiring any secret or leaked credential) can obtain at least one validly-signed webhook body/HMAC pair and replay it with a modified shop header. No access token, `api_secret_key`, or privileged access is required.

### Recommendation
Include the shop/tenant identity as part of the signed content that `HmacValidator` verifies for webhooks, or otherwise cryptographically bind the `shop` header to the signature (e.g., verify the header value returned by Shopify's `X-Shopify-Shop-Domain` is intrinsically covered by the same HMAC verification, and document/require that consuming apps additionally verify shop domain against the installed/known shop before trusting the payload). At minimum, update `Utils::VerifiableQuery`/`HmacValidator` so any header used as an identity field for a `VerifiableQuery` implementation is part of `to_signable_string`, closing the gap between what's verified and what's acted upon.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, obtaining the app's shared `api_secret_key`-signed webhook deliveries as normal.
2. Attacker configures/triggers a webhook topic whose body content they control or can predict (e.g. via a Shopify action they perform in their own store), capturing `(raw_body, X-Shopify-Hmac-Sha256)` from a genuine delivery.
3. Attacker replays this exact `raw_body` and `hmac` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` only look at the body; `HmacValidator.validate` succeeds since it never checks `shop`.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, and the app processes attacker-controlled data as authentic input from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
