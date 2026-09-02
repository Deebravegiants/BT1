This confirms the finding: `WebhookMetadata#shop` is documented and used by host apps as the tenant identity for webhook processing, e.g. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))`, but `shop` comes from an unsigned header while the HMAC only covers the raw body.

### Title
Webhook `shop` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then trusts a separate, unsigned header to determine which shop/tenant the webhook belongs to. This breaks the intended binding of `shop == cryptographically-authenticated-tenant`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any signature coverage [2](#0-1) .

`Registry.process` validates only that HMAC via `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, to_signable_string)` — i.e., HMAC over the body only — and compares against the `hmac-sha256` header [3](#0-2) . After this check passes, `process` immediately builds `WebhookMetadata` using `request.shop`, which is the unauthenticated header value, and dispatches it to the app's registered handler as the tenant identity for the event [4](#0-3) .

The gem's own documentation instructs host apps to trust `data.shop` as "The shop domain of the webhook" and to use it directly for tenant-scoped work (e.g., enqueuing jobs keyed by `shop_domain: data.shop`) [5](#0-4) . This is the intended trust contract of `WebhookMetadata#shop` [6](#0-5) .

The identity binding that should hold is: `HMAC-authenticated bytes == bytes used to determine tenant (shop)`. Here that equality is broken: the HMAC only authenticates `raw_body`, while `shop` is taken from a header outside the MAC's coverage. Any unprivileged party who has legitimately installed the app on **their own** shop will receive genuine webhooks (valid body + valid HMAC) from Shopify for their own tenant. Because the `shop-domain` header is not part of the signed material, that same attacker can replay the identical `(raw_body, hmac-sha256 header)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never inspects `shop`), and the handler receives `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an app that uses `data.shop` (as documented) to decide which tenant's records/access token/webhook data to act on can be made to process attacker-supplied webhook bodies "as" an arbitrary victim shop, without needing the app's `client_secret` or any victim credentials. Depending on how the host app uses this value (e.g., looking up the victim's stored access token by shop and performing actions, or writing/merging data into the victim tenant's records keyed by `shop`), this can lead to cross-tenant data corruption or unauthorized actions attributed to the wrong merchant.

### Likelihood Explanation
Requires only an unprivileged attacker who can install the app on any shop (a normal action any merchant can take) to obtain one legitimate `(raw_body, hmac)` pair, then send a forged HTTP request directly to the app's public webhook endpoint with a different `shop-domain` header. No secret material, session, or victim interaction is required — moderate/high likelihood for any host app that trusts `WebhookMetadata#shop` for tenant routing, which is exactly the documented usage pattern of this gem.

### Recommendation
Include the shop domain (and other origin-identifying headers, e.g. `webhook-id`, `topic`) as part of the HMAC-signed material in `Request#to_signable_string`, or otherwise cryptographically bind the `shop` header to the payload before exposing it via `WebhookMetadata`, so that `Utils::HmacValidator.validate` fails if the `shop-domain` header is altered independently of the signed body.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`), receiving from Shopify a POST with body `B` and header `X-Shopify-Hmac-Sha256: H = HMAC(client_secret, B)`.
2. Attacker sends a new POST directly to the app's public webhook endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` parses `shop` from the forged header [2](#0-1) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds [7](#0-6) .
5. The handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, and any host-app logic keyed on `data.shop` operates under the wrong tenant identity.

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

**File:** docs/usage/webhooks.md (L12-29)
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
