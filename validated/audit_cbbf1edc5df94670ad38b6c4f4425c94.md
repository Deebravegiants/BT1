This confirms the finding: the docs explicitly describe `Registry.process` as verifying "the request did indeed come from Shopify" (`docs/usage/webhooks.md` lines 125), and pass `data.shop` directly to the handler as a trusted field (`docs/usage/webhooks.md` lines 12-14, 25-26), while the actual cryptographic verification in `Utils::HmacValidator.validate` only covers the raw body bytes, not the shop domain header.### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
### Finding Description
The bug-class hint in the report is: "a field is acted on but not covered by the HMAC." In `ShopifyAPI::Webhooks::Request`, the value used to authenticate/route a webhook is `hmac`, computed over `to_signable_string`, which returns only `@raw_body`: [1](#0-0) 

The `shop` attribute, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header and is never included in the signable string: [2](#0-1) 

`Registry.process` validates only this HMAC (over the body) and then constructs `WebhookMetadata` with `shop: request.shop`, which is handed to the app's handler as trusted, authenticated data: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` const with no additional binding to the HMAC: [4](#0-3) 

The gem's own documentation instructs developers to treat `Registry.process` as verifying "the request did indeed come from Shopify," and to trust `data.shop` as the shop identity for the webhook: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `hmac == HMAC(secret, raw_body ∥ shop)` (or at minimum, the `shop` used by the handler should be provably tied to the same request whose HMAC was validated). Instead, what is actually verified is `hmac == HMAC(secret, raw_body)`, and `shop` is taken from an out-of-band, attacker-controlled header. This is exactly the "identity binding broken" pattern from the report: `_updateRewardForAllTokens` (the security-relevant action) is decoupled from `withdraw()`'s state change; here, HMAC verification is decoupled from the `shop` value used by the handler.

### Impact Explanation
Because a merchant can install the same app and legitimately receive validly-HMAC-signed webhooks for their own shop, an attacker who controls a store with the app installed can capture a real `raw_body` + valid `hmac` pair from their own webhooks, then replay that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes (only the body is checked), and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain. If the host application uses `data.shop` (as the documented example explicitly does: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) to look up the victim's stored session/access token and perform actions or persist attacker-supplied `data.body` under the victim's tenant, this results in cross-tenant data corruption/access — one tenant's webhook payload being attributed to another tenant, without needing the app's `client_secret` or any token. This matches the Critical "cross-tenant access" bucket.

### Likelihood Explanation
Exploitation only requires: (1) attacker has (or creates) a shop with the same app installed to receive one legitimately signed webhook of any subscribed topic, and (2) attacker can send arbitrary HTTP headers to the app's public webhook endpoint (trivial, since the endpoint is a normal Rails/Sinatra route as shown in the docs). No `api_secret_key`, access token, or privileged access is required — the attacker uses only their own store's genuine webhook traffic. The gem's documented pattern (`webhooks.md`) actively encourages using `data.shop` for tenant identification without warning that it is unauthenticated, making this reachable by any unprivileged internet user who can operate a shop instance of the target app.

### Recommendation
Bind the `shop` domain (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the request whose signature was checked, e.g. by having `VerifiableQuery#to_signable_string` for webhook requests include the shop domain header alongside the body, and rejecting the request if this composite does not match. At minimum, document prominently in `docs/usage/webhooks.md` that `data.shop` is not covered by HMAC verification and must not be used alone to resolve tenant/session state without corroborating it against records already trusted by the app (e.g., cross-checking against `webhook_id` deduplication combined with a shop that is known to have registered that specific webhook subscription).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and subscribes to a webhook topic (e.g., `orders/create`) via the app's normal registration flow.
2. Shopify sends a legitimately signed webhook to the app for `attacker-shop.myshopify.com`: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this exact `(B, HMAC)` pair (they receive it because it's their own webhook, or they run a local proxy/webhook capturer on their own store) and replays it to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-hmac-sha256" => same_hmac})` is constructed.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`), unaffected by the header change.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled webhook content as if it belonged to `victim-shop.myshopify.com`.

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
