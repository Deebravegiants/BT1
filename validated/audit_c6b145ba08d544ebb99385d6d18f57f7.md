### Title
Webhook `shop` domain is not covered by HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once the HMAC over the raw body validates, but the `shop` field it hands to the app's handler is read from an HTTP header that is **not** part of the signed material. An unprivileged user who owns/controls one shop that has the target app installed can capture a single legitimately-signed webhook delivery and replay it with the `X-Shopify-Shop-Domain` header changed to a victim shop, and the gem will report it as a valid, authenticated webhook for the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` are computed strictly from the raw HTTP body: [1](#0-0) [2](#0-1) 

`shop` is read from a separate, unsigned header (`shopify-shop-domain`/`x-shopify-shop-domain`): [3](#0-2) 

`Registry.process` validates the HMAC (which only proves the *body* bytes were produced with the app's secret at some point), then forwards `request.shop` unchecked into `WebhookMetadata`, which is what the app handler is documented to trust as the tenant identifier: [4](#0-3) 

The `HmacValidator` confirms the body signature but has no knowledge of, or binding to, the `shop` header at all: [5](#0-4) 

The identity binding this breaks is: **shop authenticated by the HMAC-signed body ≠ shop asserted in `WebhookMetadata.shop` consumed by the app**. Documentation explicitly instructs developers to key tenant-scoped work off `data.shop`: [6](#0-5) 

Because the HMAC never covers the shop-domain header, any attacker who can obtain one authentic body+HMAC pair (trivially available to them for their own installed shop, since Shopify delivers webhooks to an endpoint they control) can resubmit that exact body/HMAC pair while substituting an arbitrary victim shop domain in the header. `Registry.process` will validate the HMAC successfully (the body is unchanged) and hand the handler `WebhookMetadata.new(shop: "<victim>.myshopify.com", body: <attacker-controlled JSON>, ...)`, i.e., attacker-controlled data attributed to a tenant the attacker does not control.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook authenticity: an unprivileged shop owner can inject attacker-chosen webhook payloads that the app processes as belonging to a different, victim shop. Since the documented handler pattern uses `data.shop` to route storage/queue updates per tenant, this enables cross-tenant data injection/corruption without any credentials belonging to the victim — a cross-tenant access impact.

### Likelihood Explanation
Any user who can install the app on a shop they control (a normal, unprivileged onboarding flow) can trigger a real webhook for that shop, capture the raw body and its valid `x-shopify-hmac-sha256` value, and replay it against the same webhook endpoint with a forged `x-shopify-shop-domain` header. No secret key, session, or token is required — the exploit only needs one authentic webhook that the attacker owns and network access to the app's public webhook callback URL.

### Recommendation
Bind the `shop` identity to the HMAC-verified payload rather than trusting an unsigned header. Options:
- Include the shop domain (and other identity headers Shopify sends) in the signable payload used for HMAC verification, and reject requests where it doesn't correspond to a shop known to have the currently-registered webhook/session.
- Cross-check `request.shop` in `Registry.process` against the shop associated with the currently active session/registration for that webhook topic before invoking the handler, rejecting mismatches.
- At minimum, document loudly that `WebhookMetadata.shop` is not itself covered by the HMAC and must not be trusted as an authentication boundary without additional verification (e.g., checking it against a known installed-shop list) in the host application.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal, unprivileged onboarding).
2. Attacker triggers any subscribed webhook topic (e.g. `products/update`) for their own shop, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header value sent by Shopify to the app's callback URL (attacker controls network path/inspection to their own endpoint, or uses Shopify's webhook resend/test feature and a proxy).
3. Attacker resends the exact same raw body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. In `ShopifyAPI::Webhooks::Registry.process`:
   - `Utils::HmacValidator.validate(request)` succeeds because it only hashes `raw_body` [2](#0-1) .
   - The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)` [7](#0-6) .
5. Any app that stores/queues work keyed by `data.shop` (per the gem's own documented handler example) now processes attacker-controlled data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
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

**File:** docs/usage/webhooks.md (L10-29)
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
    end
  end
end
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
