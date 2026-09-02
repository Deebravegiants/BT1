### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the unauthenticated `X-Shopify-Shop-Domain` header, while `HmacValidator` only verifies the raw HTTP body. Any user who can get one valid HMAC-signed webhook body from the app (e.g., by installing the app on their own store and triggering an event) can replay that body to the app's webhook endpoint with the `shop-domain` header changed to point at a different, victim shop. `Registry.process`/`HmacValidator.validate` will accept it because the signature check never covers the header that identifies which tenant the event belongs to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic`/`#webhook_id`/`#api_version` are all read straight from HTTP headers that are not part of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the signature only over `to_signable_string` (the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

The equality the gem is implicitly relying on is:
`shop used to route/attribute the webhook (Request#shop, from header)` == `shop the HMAC actually authenticates (none — HMAC only covers body bytes)`.

Because the app's `client_secret` (and therefore the HMAC key) is shared across every shop that installs the app, any shop that has legitimately installed the app can produce a body + valid HMAC pair for itself, then submit it to the app's webhook callback URL with the `X-Shopify-Shop-Domain` header rewritten to a different, victim shop domain. The signature still validates (it only proves the body was signed with the app's secret, not which shop it was signed for), so `ShopifyAPI::Webhooks::Registry.process` will invoke the app's handler with `data.shop` set to the attacker-chosen victim shop, as documented: [4](#0-3) [5](#0-4) 

This is the same class of bug as the ERC721F report: an access/identity check (`transferFrom`'s owner/allowance check) is bypassed because a different entry point (`safeTransferFrom`) performs the sensitive action without re-checking the binding. Here, the sensitive binding — "this event body was signed for shop X" — is never actually established by the gem; the header claiming shop X is trusted without being covered by the same authentication primitive (the HMAC) that is supposed to prove authenticity.

### Impact Explanation
Any host application that uses `Request#shop` (or the `data.shop` field passed to `WebhookHandler#handle`) to decide which merchant a webhook event belongs to — to look up that merchant's session/access token, update per-shop billing/state, or attribute the event — can be made to process a fully attacker-controlled, validly-signed body under a victim shop's identity. Depending on what the host does with the webhook, this enables cross-tenant data corruption or state confusion (e.g., forging a victim's uninstall/subscription/order webhook, or resetting/poisoning per-shop state keyed by `shop`), which matches the "cross-tenant access" Critical-impact category, since the boundary broken is between different merchants (tenants) of the same app.

### Likelihood Explanation
The prerequisite is only that the attacker be able to install (or already have installed) the app on a store they control — an ordinary, unprivileged merchant action, not a privileged account or leaked credential. No `api_secret_key`, access token, or TLS interception is required; the attacker only needs to trigger a real event on their own store to obtain a genuinely-signed body/HMAC pair, then replay it with a modified `shop-domain` header. This is straightforward to automate and requires no cooperation from Shopify or the victim.

### Recommendation
Bind the tenant identity into the authenticated payload before trusting it: either include the shop-domain header in the HMAC-signed material (`to_signable_string`), or cross-validate `Request#shop` against a shop identifier embedded in the JSON body itself (most Shopify webhook payloads include the resource/shop context) before dispatching to handlers. At minimum, document prominently that `Request#shop` is unauthenticated and must not be used by itself to key access to secrets/tokens without an additional cross-check against server-side state (e.g., verifying a session already exists for that shop and that the webhook was actually requested/registered for it).

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and legitimately triggers a webhook topic the app is subscribed to (e.g., `app/uninstalled` or `orders/create`), capturing the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify computed with the app's shared `client_secret`.
2. Attacker POSTs the exact same body `B` and header `H` to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `HmacValidator.validate` recomputes `HMAC(secret, B)` and compares to `H` — it matches, since `to_signable_string` never includes the shop header.
4. `Registry.process` calls the registered handler with `data.shop == "victim.myshopify.com"` even though the payload was never generated for or by that shop, letting the attacker impersonate a webhook event on behalf of an arbitrary tenant.

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

**File:** docs/usage/webhooks.md (L10-30)
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
```

**File:** docs/usage/webhooks.md (L123-136)
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
```
