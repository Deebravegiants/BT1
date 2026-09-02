Confirmed: the documented API explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and that `data.shop` is "The shop domain of the webhook" [2](#0-1) , implying `shop` is treated as an authenticated, trustworthy field. This confirms the gap: `shop` is read straight from the `shopify-shop-domain` header while only `@raw_body` is HMAC-signed.

### Title
Webhook `shop` domain is not covered by HMAC, allowing cross-tenant webhook spoofing via header substitution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw JSON body against the `hmac-sha256` header, but the `shop` (`shop-domain` header), `topic`, `webhook_id`, and `api_version` are never included in the signed payload or otherwise validated. Since the gem documents `data.shop` as a trusted, verified identifier passed to the host app's webhook handler, an attacker who legitimately installs the app on their own store can capture a genuine, validly-signed webhook, then replay the identical body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header to a victim shop's domain. `ShopifyAPI::Webhooks::Registry.process` accepts this because it only checks `Utils::HmacValidator.validate(request)`, which is computed purely from `to_signable_string` = `@raw_body`.

### Finding Description
The HMAC binding the gem asserts is: `hmac == HMAC(secret, raw_body)` [3](#0-2) . The identity used downstream, however, is `shop == header("shopify-shop-domain")` [4](#0-3) , and this value is never included in `to_signable_string`. The equality the gem needs but does not enforce is:

`shop_used_by_handler == shop_that_the_HMAC_actually_authenticates`

Since the HMAC authenticates only `raw_body`, and `raw_body` for a given topic/payload can be identical across many merchants' identical resource states (or replayed verbatim), the `shop` value is effectively unauthenticated attacker-controlled metadata riding alongside an otherwise-valid signature.

`Registry.process` validates only the HMAC and then immediately trusts `request.shop` to build `WebhookMetadata`, handing it to the host app's handler: [5](#0-4) . The public documentation instructs integrators that `process` "will verify the request did indeed come from Shopify" and describes `data.shop` as an authoritative field, with example handlers directly keying persistence/business logic off of it (`shop_domain: data.shop`) [6](#0-5) . Nothing in the gem's public API or documentation tells integrators they must independently re-verify that the `shop` header actually corresponds to a shop entitled to send the given signed body — the gem's own `process` claims to do full verification.

### Impact Explanation
This breaks the tenant boundary the webhook system is supposed to enforce. Any internet user who can self-install the app on their own trial/dev store (a normal, unprivileged flow) obtains a stream of genuinely-signed webhooks for their own shop. By replaying the exact `raw_body` + `hmac-sha256` header pair while swapping only the `x-shopify-shop-domain` header, they can make the app process the resulting `WebhookMetadata` as if it originated from an arbitrary victim shop, since the gem performs no cross-check between the signed bytes and the shop claim. Depending on how the host app's handler uses `data.shop` (e.g., to select which tenant's DB row to update, sync inventory, or trigger fulfilment/order actions), this enables cross-tenant data corruption or action injection against a shop the attacker does not control, satisfying the "cross-tenant access" criteria.

### Likelihood Explanation
Likelihood is meaningful: obtaining a validly-signed webhook for one's own shop is trivial for anyone able to install a public app (no special privileges, no leaked secret required), and replaying an HTTP POST to the app's public webhook callback endpoint with a modified header is straightforward. The main constraint is that the attacker needs a `raw_body` whose HMAC they possess and that is also meaningful/impactful when misattributed to a different shop (e.g., a webhook body containing an ID or payload the victim's handler will act upon, or a topic like `app/uninstalled` whose body content doesn't need to vary per shop).

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise validate the `shop-domain` header against a value the gem controls independently of attacker-supplied headers (e.g., cross-check against the shop associated with the resolved session/registration, or include the header set in the signable string if Shopify's webhook signing were extended to cover headers). At minimum, update `Webhooks::Request#to_signable_string` so it is not solely `@raw_body`, and update `docs/usage/webhooks.md` to explicitly warn integrators if `shop` cannot be cryptographically bound, so they don't treat `data.shop` as verified.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers for a webhook topic, e.g. `orders/create`.
2. Shopify sends a legitimately signed webhook to the app's callback: body `B`, header `x-shopify-hmac-sha256: H` (valid for secret and `B`), `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the same `POST` to the app's webhook endpoint, keeping `raw_body = B` and `x-shopify-hmac-sha256 = H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares to `H` — this succeeds because `B` and `H` are untouched [7](#0-6) .
5. `Registry.process` builds `WebhookMetadata` with `shop: request.shop` = `"victim-shop.myshopify.com"` and invokes the host app's handler [8](#0-7) , causing the app to act as though the victim shop sent this webhook.

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L19-30)
```markdown
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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```

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
