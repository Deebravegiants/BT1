### Title
Webhook `shop` field is not covered by the HMAC signature, allowing shop/tenant spoofing in `ShopifyAPI::Webhooks::Registry.process` - ([File: lib/shopify_api/webhooks/request.rb](), [File: lib/shopify_api/webhooks/registry.rb]())

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity by checking only the HMAC over the raw request body, then trusts the `shop` value taken from an unauthenticated HTTP header and forwards it to the app's handler as an authoritative tenant identifier. Because the app's `api_secret_key` is shared across every shop that installs the app, any merchant who can obtain one authentic (validly-signed) webhook body for their own shop can replay that body with a different `shop-domain` header value and have it accepted as an authentic webhook "from" a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is completely outside the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC strictly over `verifiable_query.to_signable_string` (the body), never over headers: [3](#0-2) 

`Registry.process` uses this same validator, and once it returns `true`, unconditionally builds `WebhookMetadata` using `request.shop` (the unauthenticated header) and hands it to the app's registered handler as trusted tenant data: [4](#0-3) 

The gem's own documentation states that `process` "will verify the request did indeed come from Shopify and then call the specified handler for that webhook," and explicitly promises `data.shop` as "The shop domain of the webhook" for use by the handler: [5](#0-4) [6](#0-5) 

This is the exact analog of the reported bug class: a field that is *acted on* (the `shop` value used to route/attribute the webhook to a tenant) is not covered by the HMAC that is supposed to bind the whole request to that tenant. The equality the gem should enforce is:
`shop_bound_by_hmac == shop_used_by_handler`
but instead it only enforces `hmac(body) == received_hmac`, with `shop` supplied independently and unauthenticated.

Because Shopify apps typically use a single `api_secret_key` for *all* installations (it is the app's secret, not a per-shop secret), a legitimate merchant who installs the app on Shop A receives real webhooks with valid HMACs computed with that same shared secret. That attacker-controlled merchant can capture a real `(body, hmac)` pair from their own shop's webhook traffic and re-POST it to the app's webhook endpoint with the `shopify-shop-domain` header changed to Shop B (the victim). `HmacValidator.validate` still succeeds (it never looked at the header), so `Registry.process` calls the handler with `data.shop == "shop-b.myshopify.com"` even though the payload was never sent by or for Shop B.

### Impact Explanation
If the host application follows the gem's documented pattern and uses `data.shop` to look up the tenant/session record to write into (e.g., updating orders, inventory, customer data, or GDPR redaction state), an attacker who is a legitimate but unprivileged merchant of the app can inject attacker-chosen webhook bodies that are attributed to a different, victim tenant. This is a cross-tenant integrity/confusion issue: data belonging to Shop B can be corrupted, or actions intended for Shop B can be triggered, using only content generated for the attacker's own Shop A installation. No access token, session cookie, or `api_secret_key` value is ever obtained or required by the attacker — they only need to be a normal, unprivileged app user (any store owner can install a public app).

### Likelihood Explanation
Likelihood is moderate: the attacker must operate their own store with the target app installed (a low bar for any distributed/public Shopify app), capture one authentic webhook body/HMAC pair addressed to their own shop (trivial, since they receive their own webhooks), and replay it to the app's public webhook endpoint with a modified shop-domain header. No secrets or elevated privileges are required, and the gem provides no mechanism or warning that `data.shop` needs independent verification against a known/registered shop before being trusted.

### Recommendation
Bind the `shop` (and other identity-relevant headers used by the handler) into the value that is HMAC-verified, or otherwise cross-check `request.shop` against an independently-authenticated source (e.g., the shop associated with the specific webhook subscription/session, not a bare header) before constructing `WebhookMetadata`. At minimum, update the documentation to make explicit that `data.shop` is not covered by the HMAC check and must not be trusted as an authenticated tenant identifier without further verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, triggering a real webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker replays the exact same `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and matches `H` — validation passes (see `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` and invokes the app's handler (`lib/shopify_api/webhooks/registry.rb:198-199`), which believes the event genuinely originated from `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L123-135)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
