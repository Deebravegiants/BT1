### Title
Webhook `shop-domain` header is trusted for tenant attribution without being covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating only the HMAC over the raw body, then unconditionally trusts the `shop-domain` (and `topic`, `webhook_id`, `api_version`) HTTP headers — none of which are covered by that HMAC — to build the `WebhookMetadata` passed to the host application's handler. The tenant-identifying field (`shop`) that the handler is documented to rely on for tenant attribution is never bound to the cryptographic signature that authenticates the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

All other request fields, including `shop`, are pulled straight from attacker/network-controlled HTTP headers without any cryptographic binding: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers `raw_body`) and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to construct `WebhookMetadata`, which is handed to the app-defined handler: [3](#0-2) 

The documented and expected use of `WebhookMetadata#shop` is for tenant identification/attribution in the host application (e.g. looking up the shop's session, enqueuing per-shop background jobs): [4](#0-3) 

The binding that should hold is: `shop authenticated by the app's shared secret` == `shop attributed to the resulting business action`. Because the HMAC only signs `raw_body` and the app's `api_secret_key` is a single secret shared across *all* shops/tenants installed on the app (this is how Shopify signs webhooks — one app secret, not a per-shop secret), any actor who can obtain one valid `(raw_body, hmac)` pair for *any* shop (including their own, if they operate/install the app on a shop they control) can replay that exact body+HMAC while substituting an arbitrary `shop-domain` header for a victim shop. `Utils::HmacValidator.validate` will pass because it never inspects the header values: [5](#0-4) 

The handler then receives `data.shop` = the victim's domain, `data.body` = the attacker's chosen (or replayed) body, satisfying an authenticated-looking cross-tenant event.

### Impact Explanation
This breaks the tenant boundary the host application relies on. An unprivileged user who can install the app on their own shop (or who has captured any single legitimate webhook body+signature) can forge webhook deliveries that the app attributes to a different, victim tenant. Depending on how the host app's handler code uses `data.shop` (as most integrations do, per the documented pattern of enqueuing jobs keyed by `shop_domain`), this can result in cross-tenant data corruption, triggering of tenant-scoped side effects (e.g., order/product updates, deletions, notifications) attributed to a shop the attacker does not control. This matches the "cross-tenant access" criterion for Critical severity, since the identity binding between the authenticated signature and the tenant identity used for business logic is broken entirely inside this gem's `Registry.process`/`Request` code path, not merely due to host-app misuse.

### Likelihood Explanation
Likelihood is non-trivial because Shopify signs all webhooks for an app with the single app-level secret, and the body is not otherwise secret or unique to a shop — many webhook bodies (e.g., a `themes/publish` event with generic content, or replayable low-entropy payloads) may be reused or predictable, and at minimum an attacker who legitimately installs the app on their own store receives real valid `(body, hmac)` pairs they fully control the timing/content of, and can then relabel with a victim's `shop-domain` header. No access to `api_secret_key`, access tokens, or TLS interception is required — only the ability to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers, which is exactly the "unprivileged internet user" threat model here.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the signed payload used for verification (e.g. require the host app pass the raw Shopify webhook headers such that verification recomputes/compares the signature together with a shop allow-list per-registration, or verify that `request.shop` matches the shop context under which the corresponding subscription was registered) rather than trusting them merely because the HMAC over the body succeeded. At minimum, `Registry.process` should require and validate a caller-supplied expected shop (from the session/tenant context already known to the app) against `request.shop` before invoking the handler, and document clearly that `data.shop` is unauthenticated metadata.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to (e.g. `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify legitimately computed with the app's `api_secret_key` over `B`.
2. Replay a request to the app's webhook endpoint with the same `raw_body: B` and `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com` and desired `x-shopify-topic`.
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `HMAC(api_secret_key, B) == H` (`lib/shopify_api/utils/hmac_validator.rb:26-31` via `to_signable_string` returning only the body, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to perform tenant-scoped actions against the victim shop using attacker-supplied/replayed body content.

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

**File:** docs/usage/webhooks.md (L10-26)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
