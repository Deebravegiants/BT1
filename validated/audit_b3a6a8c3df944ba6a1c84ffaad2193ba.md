This confirms the docs explicitly document `data.shop` as "The shop domain of the webhook" — the field apps are told to use for tenant attribution (`shop_domain: data.shop` in the example handler). This confirms the finding: `data.shop` is documented as a trusted tenant-identifying field, yet it derives from an unauthenticated header not covered by the HMAC.

### Title
Webhook `shop` field used for tenant attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only that HMAC-over-body, then passes the header-derived `shop` value straight into `WebhookMetadata`, which the gem's own documentation instructs app developers to use as the tenant identifier (`shop_domain: data.shop`) for routing/storing webhook data.

### Finding Description
The HMAC binding breaks the identity equality: `HMAC(raw_body)` covers `raw_body` only, but `WebhookMetadata#shop` (acted on by the host app for tenant attribution) is taken from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is *not* part of the signed material.

- `Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 
- `Request#shop` is read verbatim from a header with no cross-check against the signed body: [2](#0-1) 
- `HmacValidator.validate` only verifies `verifiable_query.hmac` against `to_signable_string` (i.e., the body), never the headers: [3](#0-2) 
- `Registry.process` validates HMAC and then forwards the unauthenticated `request.shop` straight into the handler's `WebhookMetadata`: [4](#0-3) 
- The gem's own documentation tells integrators to trust `data.shop` as "The shop domain of the webhook" and use it for shop-scoped routing (`shop_domain: data.shop`): [5](#0-4) 

Because every shop installed on a given app shares the same `api_secret_key` (the HMAC key), any merchant who has installed the app can trigger a legitimate webhook for their own shop, capture the valid `(raw_body, hmac)` pair, and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. The HMAC check still passes (it only checks the body), but `WebhookMetadata#shop` now reports the attacker-chosen victim shop while the body content actually belongs to the attacker's own shop.

### Impact Explanation
This breaks the tenant boundary the library's documented API relies on: `shop` (attacker-controlled header) ≠ `shop that produced the signed body` (attacker's own installed shop). Any app that follows the gem's documented pattern of using `data.shop` to scope where webhook data gets written/updated (e.g., `perform_later(shop_domain: data.shop, webhook: data.body)`) can be made to attribute one merchant's data/events to a different merchant's tenant — a cross-tenant data confusion/injection primitive, satisfying the Critical "cross-tenant access" impact category, since it is a direct consequence of this gem's own request/HMAC design rather than misuse by the host app.

### Likelihood Explanation
Any actor who has installed the app on at least one shop (a low-privilege, unauthenticated-relative-to-other-tenants position) can mount this attack with no additional secrets: they only need a raw HTTP client to replay their own legitimately-received webhook with a modified header. No access to `api_secret_key`, tokens, or victim credentials is required.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed material, or otherwise cryptographically tie the header-derived shop to the signed payload — e.g., include the shop domain in `to_signable_string`, or require the handler to independently verify that the `shop` matches a value embedded in `body` (where Shopify includes shop identifiers) before trusting it for tenant routing. At minimum, update `Request#to_signable_string` to incorporate the `shop-domain` header so `HmacValidator.validate` fails when it has been tampered with in transit.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate `orders/create` webhook:
   - Headers: `x-shopify-hmac-sha256: <valid HMAC over body B>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`
   - Body: `B` (attacker's own order data)
2. Attacker resends the exact same body `B` and HMAC header to the app's public webhook endpoint, but replaces the shop header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: tampered_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares it to the (valid, replayed) header value — validation succeeds because `to_signable_string` only returns `B`.
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, and any app following the documented pattern (`perform_later(shop_domain: data.shop, webhook: data.body)`) stores/acts on attacker-supplied order data under the victim shop's tenant.

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
