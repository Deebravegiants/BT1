This confirms the vulnerability: the library's own documentation states `data.shop` — "The shop domain of the webhook" — is meant to identify the tenant, and the documented usage example directly keys application logic on it (`data.shop`), yet this field is parsed straight from an HTTP header that carries no cryptographic binding to the HMAC-verified bytes.

### Title
Webhook tenant identity (`shop`, `topic`) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the tenant-identifying `shop` (and `topic`/`webhook_id`) values that are handed to the application's handler are read from unauthenticated HTTP headers that are never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` verifies the HMAC exclusively against that signable string [2](#0-1) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all parsed directly out of request headers with zero cryptographic verification [3](#0-2) .

`Registry.process` then trusts these unverified header values to construct the tenant identity passed to the app's handler: `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, gated only by the body-HMAC check [4](#0-3) . The gem's own documentation confirms `data.shop` is meant to be trusted as "The shop domain of the webhook" and shows it being used directly to key business logic (`shop_domain: data.shop`) [5](#0-4) .

The broken binding, stated as an equality that does not hold:
`bytes_covered_by_hmac (raw_body)` ≠ `bytes_used_as_tenant_identity (shop header, topic header)`

Because a Shopify app's `client_secret` (the HMAC key) is shared across **every merchant install of that app**, any unprivileged user can install the same public app on their own (even free/dev) store. Shopify will then deliver them legitimately-HMAC-signed webhook requests, i.e. valid `(raw_body, hmac)` pairs signed with the app's shared secret. Because `shop`/`topic` are outside the signed payload, that attacker can replay the exact same body+HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header with a victim shop's domain. `Registry.process` will accept it (the HMAC over the body is still valid) and dispatch it to the handler as if it originated from the victim tenant, since `request.shop` is never cross-checked against anything HMAC-covered.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook authenticity: an attacker with no privileged access to the victim tenant, no leaked credentials, and no interception capability can make the app process attacker-controlled body content while attributing it to an arbitrary victim `shop`. Depending on how the host app persists/acts on webhook data (common pattern: upsert order/customer/product records keyed by `data.shop`), this enables cross-tenant data injection/corruption — qualifying as Critical (cross-tenant access).

### Likelihood Explanation
Likelihood is realistic: the attacker only needs to be a normal merchant who installs the same publicly-distributed app (a routine, unprivileged action requiring no secrets), then capture one of their own legitimately-delivered webhooks (trivially observable on their own endpoint or via any HTTP proxy on traffic they control) and replay it with a modified `shop`/`topic` header to the app's public webhook URL.

### Recommendation
Bind the tenant/topic identity into the signed material, or verify it out-of-band: e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string` (requiring Shopify to sign over them, which it already computes server-side per delivery), or have `Registry.process` independently confirm the `shop` header corresponds to a shop with an active, registered webhook subscription for that specific `webhook_id`/topic before dispatching to the handler, rather than trusting the header value as-is.

### Proof of Concept
1. Attacker installs the target public app on their own Shopify dev store (`attacker-shop.myshopify.com`), obtaining a normal merchant install — no special privileges needed.
2. Attacker triggers an event (e.g. `orders/create`) on their own store, causing Shopify to POST a legitimately HMAC-signed webhook to the app's public webhook endpoint:
   ```
   POST /webhook
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC over raw_body, signed with the app's shared client_secret>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   { "id": 1, ... attacker-controlled order body ... }
   ```
3. Attacker captures this exact `(raw_body, X-Shopify-Hmac-Sha256)` pair and resends it directly to the same endpoint, only changing the shop header:
   ```
   POST /webhook
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same valid HMAC as above>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   { "id": 1, ... same attacker-controlled body ... }
   ```
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` succeeds because it only checks the HMAC against `raw_body`, which is unchanged [6](#0-5) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker-controlled>, ...)`, causing the app to process attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
