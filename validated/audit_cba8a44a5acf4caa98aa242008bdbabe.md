### Title
Webhook shop-domain spoofing via HMAC scope gap — the `X-Shopify-Shop-Domain` header is not covered by the HMAC that `ShopifyAPI::Webhooks::Registry.process` verifies ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once the raw body's HMAC matches, and then trusts the `shop`/`shop-domain` header verbatim to identify which tenant the event belongs to. But the HMAC only ever covers the raw JSON body — the shop-domain header used to attribute the event to a specific merchant is never part of the signed material. This is the same class of bug as the reported PearVault issue: an identity-relevant field (the tenant/depositor) is decoupled from the value that is actually checked (the receiver/HMAC), letting an attacker substitute identities after the check has already passed.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then forwards `request.shop` straight to the app's handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes and compares the signature purely over `verifiable_query.to_signable_string`, i.e. the body — never the shop header: [4](#0-3) 

The gem's own documentation tells integrators that calling `Registry.process` "will verify the request did indeed come from Shopify" and hands the handler a trusted `data.shop` "shop domain of the webhook" field: [5](#0-4) [6](#0-5) 

The equality the gem should enforce is: *the shop bound by the HMAC-verified payload == the shop attributed to the event.* Instead it enforces only *HMAC(body) == received signature*, and separately trusts an unauthenticated header for the shop. Any actor who can obtain one legitimate `(raw_body, hmac)` pair for their own shop (e.g., by observing their own app's webhook traffic — no special privilege required) can replay that exact body+HMAC pair to the same endpoint while swapping the shop-domain header to a different merchant's domain that is also installed on the app. `HmacValidator.validate` still passes (it never looked at the header), and `WebhookMetadata.shop` now falsely identifies a different tenant.

### Impact Explanation
This breaks the shop/tenant identity binding that host applications rely on when they use this gem's webhook handling. Depending on how the topic's body is otherwise plausible for a different shop, a low-privileged actor (merely another app installer) can inject events — e.g., `app/uninstalled`, `shop/redact`, plan-change or compliance topics — attributed to a shop they do not operate, corrupting per-tenant state, billing gating, or data-deletion logic keyed off `data.shop`. This is a cross-tenant identity confusion vulnerability enabled entirely by this gem's verification logic, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires no `api_secret_key`, no access token, and no privileged account — only an ordinary app installation to observe one legitimate webhook delivery and replay it with a modified header, which is well within reach of any unprivileged internet-connected actor who can install the target app on their own shop.

### Recommendation
Bind the shop identity into the material that is HMAC-verified, or independently re-derive/verify the shop from a source the app already trusts (e.g., cross-check `shop` against the session/tenant that a stored webhook registration expects, or include the shop domain in the signable string used to compute/verify the HMAC) before handing `WebhookMetadata` to the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a genuine webhook (any topic) to the app's endpoint; attacker captures the exact `raw_body` and the `X-Shopify-Hmac-Sha256` value Shopify sent.
2. Attacker crafts a new HTTP request to the same webhook endpoint using the identical `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (a shop also installed on the app).
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers (`lib/shopify_api/webhooks/request.rb:45-63`), and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:27-31`) — validation succeeds.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` set to `victim-shop.myshopify.com` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the payload actually originated from Shopify for `attacker-shop.myshopify.com`. The host app now processes attacker-controlled webhook data under the victim's tenant identity.

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
