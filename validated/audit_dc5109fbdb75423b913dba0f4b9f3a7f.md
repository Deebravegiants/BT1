### Title
Webhook `shop` field is trusted for tenant identification despite not being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity using an HMAC computed only over the raw request body, but the `shop` domain used to attribute the webhook to a tenant is read directly from an unauthenticated HTTP header and passed through to the app's handler unchecked.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate_signature` computes/compares the HMAC solely against that signable string [2](#0-1) . Meanwhile, `Request#shop` is extracted straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic binding to the HMAC at all [3](#0-2) .

`Registry.process` validates the HMAC and then immediately forwards `request.shop` (the unauthenticated field) into `WebhookMetadata`, which is delivered to the host app's handler as the tenant identifier for the event: [4](#0-3) .

The library's own documentation instructs integrators to treat `data.shop` as the authoritative shop domain for the webhook (`shop_domain: data.shop`) [5](#0-4) , i.e. this is the gem's documented, intended usage of that field for tenant-scoped processing (e.g. looking up the corresponding shop's session/access token).

The equality that should hold but does not:
`hmac_valid(raw_body, api_secret_key) == true` should imply `request.shop == <the shop the HMAC was actually generated for>`. In this gem, `request.shop` is derived from a header entirely outside the `to_signable_string` payload, so validating the HMAC provides zero guarantee about which shop the `shop` field refers to.

Because a single `api_secret_key` is shared across every shop that installs the app, any legitimate HMAC-signed webhook payload/HMAC pair captured for one tenant (or a synthetic test webhook payload the merchant can trigger from their own Shopify admin) can be replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header swapped to a victim shop's domain. The HMAC check still passes (it only checked the body), but the handler receives `data.shop` pointing at the victim tenant, and per the gem's documented pattern will use that value to key into shop-specific data/session lookups — enabling cross-tenant event injection.

### Impact Explanation
This crosses a tenant boundary: an attacker who legitimately installs the app on their own shop (an unprivileged action available to any internet user who installs a public app) can obtain a validly-HMAC-signed webhook body/HMAC pair for their own shop, then relabel it as belonging to another merchant's shop when replaying it to the app's webhook endpoint. Because the shop attribution is not bound to the signature, the app cannot distinguish "genuine event, correctly attributed shop" from "genuine event, forged attribution" — matching the Critical criterion of cross-tenant access via a broken identity binding (HMAC-verified bytes vs. the tenant-identifying field acted upon).

### Likelihood Explanation
Moderate-to-high: no secret material is required. Any user who can install the target app on a store they control can generate legitimately signed webhook traffic (e.g., via Shopify's "send test webhook" feature or by triggering a real event on their own store), capture the raw body + HMAC, and replay it against the shared public webhook endpoint with a forged `x-shopify-shop-domain` header. The only constraint is that the endpoint must be reachable and process webhooks per the gem's documented flow, which is the intended integration pattern.

### Recommendation
Bind the tenant identity to the authenticated payload rather than trusting a header untouched by the HMAC:
- Where the webhook body itself contains the shop/domain (many Shopify webhook payloads include shop-scoped identifiers), cross-check `request.shop` against a value derivable from the signed body, or
- Require host applications to independently verify that the `shop` domain is one that has actually installed the app for that specific `webhook_id`/topic combination (e.g., look up an existing, previously registered subscription/session keyed by `shop`+`webhook_id`) before trusting `data.shop`, and
- Document explicitly in `docs/usage/webhooks.md` that `data.shop` is not covered by the HMAC and must not be trusted as a sole tenant key without additional verification (e.g., matching against records created during OAuth for that shop).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and configures/receives a real webhook (or triggers "Send test notification" from the Shopify admin for a registered webhook topic), capturing the raw POST body and the `x-shopify-hmac-sha256` header sent by Shopify — both valid because Shopify itself signed them with the app's `api_secret_key`.
2. Attacker replays the exact same raw body and HMAC header to the app's public webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` [6](#0-5) , which passes because the HMAC only covers `raw_body`, unchanged from step 1.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ...)` [7](#0-6) , and per the documented usage pattern the host app treats this as a genuine event for `victim.myshopify.com`, performing shop-scoped actions/lookups keyed on the forged shop value.

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
