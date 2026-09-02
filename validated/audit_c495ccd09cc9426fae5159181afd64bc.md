### Title
Webhook shop-domain header is not covered by the HMAC, allowing cross-tenant data spoofing via the gem's documented `WebhookMetadata.shop` field - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via HMAC-SHA256 over the raw request body only. The `shop` value that the gem hands to the app's `WebhookHandler` — and which the documentation tells app authors to use as the tenant identifier — is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the HMAC-signed content. This is the same bug class as the external report: a field that is acted upon by the application (here, tenant identification) is not covered by the integrity check (here, the HMAC), breaking the intended binding `hmac == HMAC(secret, body)` with the assumption `body ⟹ shop`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived independently from a header, not from the signed body: [2](#0-1) 

`Registry.process` validates the HMAC over the `Request` object (i.e., only the body), then immediately trusts `request.shop` — sourced from the unauthenticated header — to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no additional integrity guarantee: [4](#0-3) 

The `HmacValidator` itself is generic and only checks whatever `to_signable_string` returns against the secret — it has no visibility into headers such as `shop-domain`: [5](#0-4) 

The gem's own documentation instructs developers to treat `data.shop` as the authoritative shop/tenant identifier for persisting or dispatching webhook work (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [6](#0-5) 

**Broken identity binding (as an equality):**
`HMAC-verified bytes (raw_body)` should equal `bytes that determine the tenant (shop)`, but in this implementation:
`verified(raw_body) ≠ shop_used_for_tenant_routing`, because `shop` comes from a header that is outside the HMAC's scope.

**Concrete attack path:** Any merchant who legitimately installs the app on their own store (an "unprivileged" party relative to other tenants of the same app) receives genuine Shopify webhook deliveries, each with a body and a correctly computed HMAC signed with the app's real `client_secret`, plus a `shopify-shop-domain` header set to their own shop. Because the HMAC never covers that header, the attacker can capture one such delivery and replay it to the app's webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (it only re-derives the HMAC from `raw_body`), so `Registry.process` accepts the forged request and calls the app's handler with `WebhookMetadata.shop == victim_shop` while `body` is attacker-controlled content the attacker legitimately received for their own store. Any host application following the gem's documented usage (associating incoming webhook data with `data.shop`) will store or act on attacker data under the victim tenant's identity — a cross-tenant data-integrity/confusion vulnerability rooted entirely in this gem's `Request`/`Registry` design, not in host-app misuse.

### Impact Explanation
This satisfies the "Critical - cross-tenant access" bar: an attacker who only controls their own shop's webhook deliveries can cause an app built per this gem's documented pattern to attribute forged event data to an arbitrary victim shop, because the shop identity is never bound to the signed payload.

### Likelihood Explanation
Likelihood is high for any app that follows the documented pattern of trusting `WebhookMetadata.shop` as the tenant key (as the gem's own docs recommend), since no additional shop-binding check is performed anywhere in `Request`, `HmacValidator`, or `Registry`. The only prerequisite is that the attacker controls one legitimately-installed shop, which is not a "privileged account" in the sense excluded by the rules (it does not require the app's own `client_secret`, an admin access token, or leaked credentials — only ordinary merchant-side webhook receipt capability).

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) header values in the signed payload used for HMAC verification, or otherwise cryptographically bind the `shop` claim to the verified body (e.g., require the app to look up/verify `shop` against a known, previously-established session/store record rather than trusting the header verbatim). At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header so that `HmacValidator.validate` fails if that header is altered after Shopify signs the payload.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g.:
   ```
   POST /callback/orders/create
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id":1,"note":"hello"}
   ```
2. Attacker resends the exact same body and HMAC header, but changes only the shop-domain header:
   ```
   POST /callback/orders/create
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-hmac-for-body>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id":1,"note":"hello"}
   ```
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request; `Utils::HmacValidator.validate(request)` recomputes HMAC over `raw_body` only and it matches, per: [7](#0-6) 
4. `Registry.process` calls the app handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and any handler written per the documented example persists/acts on this data under `victim-shop.myshopify.com`'s identity, despite the payload never having been signed for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
