### Title
Webhook `shop` field is trusted for tenant attribution but is excluded from the HMAC signature - cross-tenant data injection ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (tenant identity) is read from an unsigned header. `Registry.process` validates the HMAC and then hands `request.shop` straight to the app's handler as the trusted tenant identifier for the (validated) body. Because `shop` is not part of the signed bytes, an attacker who can obtain one validly-signed webhook (e.g. from their own shop that installed the app) can replay that exact body+HMAC pair while substituting a different `shop-domain` header value, and the gem will treat the payload as authentic data for the victim tenant.

### Finding Description
`Utils::VerifiableQuery` requires each verifiable request type to expose `hmac` and `to_signable_string`, and `Utils::HmacValidator.validate` simply recomputes the HMAC over `to_signable_string` and compares it to the supplied `hmac`: [1](#0-0) [2](#0-1) 

For webhooks, `Request#to_signable_string` returns only `@raw_body`; the `shop` accessor reads a header (`shop-domain`) that is never included in that signable string: [3](#0-2) [4](#0-3) 

`Registry.process` validates the HMAC of the whole `request`, then immediately forwards `request.shop` (the unsigned header) to the application handler as the authoritative tenant for that (HMAC-verified) body: [5](#0-4) 

Actually citing correctly: [6](#0-5) 

This is exactly the pattern flagged in the rules: "a field acted on but not covered by the HMAC." The equality the code implicitly assumes is:

`shop-domain header == the shop the body/HMAC was actually generated for`

but the code only proves:

`HMAC(api_secret_key, raw_body) == received_hmac`

These are not equivalent — the `shop` header can be freely modified after capture without invalidating the signature, since it is outside the signed byte range.

The gem's own documentation confirms host apps are expected to trust `data.shop` from `WebhookMetadata` as the tenant identifier coming out of `Registry.process`, with no guidance to cross-check it against anything cryptographically bound to the body: [7](#0-6) [8](#0-7) 

### Impact Explanation
An unprivileged internet user who operates (or otherwise legitimately receives webhooks from) their own shop that has installed the target app can capture one authentic, validly-signed webhook delivery (raw body + `X-Shopify-Hmac-Sha256`). Because the `shop-domain` header is not part of the signed bytes, they can replay the identical body/HMAC pair to the app's webhook endpoint while swapping in an arbitrary victim `shop-domain` value. `Utils::HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain and `body` containing attacker-controlled data from their own shop's event. Any host application that uses `data.shop` to select/update per-tenant state (the exact pattern shown in the gem's own docs, e.g. `perform_later(shop_domain: data.shop, webhook: data.body)`) will then apply attacker-influenced data under the victim's tenant record — a cross-tenant data-integrity/confusion issue that satisfies the "cross-tenant access" criterion (Critical).

### Likelihood Explanation
Exploitability requires only that the attacker be able to receive at least one legitimate webhook signed with the app's secret for *some* shop (trivial for any developer/merchant who installs the target app on their own store, which is normal unprivileged use of a public app) and the ability to POST to the app's public webhook callback URL (which is, by design, unauthenticated aside from the HMAC). No access to `api_secret_key`, access tokens, or privileged accounts is required — only a single previously-observed legitimate webhook. This is a realistic, low-effort attack path.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cryptographically/contextually verify that the `shop-domain` header matches a shop the app has an active, stored session/install for before trusting it in `WebhookMetadata`. At minimum, `Registry.process` (or the host app via documentation) should require that `request.shop` correspond to a shop with a known, previously-stored offline access token/session before dispatching to the handler, rather than trusting the raw header value implicitly once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook to the app: body `B`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`, header `X-Shopify-Hmac-Sha256: H` where `H = Base64(HMAC-SHA256(api_secret_key, B))`.
3. Attacker captures `B` and `H` (e.g., via their own logging proxy in front of their webhook endpoint).
4. Attacker crafts a new HTTP request to the app's public webhook route with the same raw body `B` and same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...with victim domain...})` is constructed; `to_signable_string` returns `B` unchanged, so `Utils::HmacValidator.validate` succeeds.
6. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled webhook content under the victim shop's tenant context.

### Citations

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L6-16)
```ruby
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
