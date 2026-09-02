### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` validates the authenticity of an incoming webhook using only the raw request body as the signable content, while the `shop` (and `topic`/`webhook_id`) values that the gem hands to the application's webhook handler are read directly from HTTP headers that are **not** part of the HMAC-signed material. This breaks the identity binding: `hmac_verified(body) == true` is treated as if it also means `shop_header == shop_that_generated(body)`, but those two are independent inputs.

### Finding Description
`Registry.process` accepts a `Webhooks::Request`, validates it with `Utils::HmacValidator.validate(request)`, and — once that passes — forwards `request.shop` (parsed from the `x-shopify-shop-domain`/`shopify-shop-domain` header) straight to the app's handler as the tenant identifier: [1](#0-0) 

The signature that is actually checked is computed only over the raw body: [2](#0-1) 

`HmacValidator.validate_signature` calls `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns `@raw_body` only — none of `topic`, `shop`, `api_version`, or `webhook_id` are included in the signed string: [3](#0-2) 

Compare this to the OAuth callback flow, where `AuthQuery#to_signable_string` explicitly folds `shop` into the signed payload so that the `shop` claim is cryptographically bound to the signature: [4](#0-3) 

For webhooks, no equivalent binding exists between the HMAC and the `shop` header. The webhook secret (`api_secret_key`/`client_secret`) is shared across *all* shops that install the same app — it is not per-shop. Consequently, any merchant who installs the app receives legitimate webhooks for their own shop and thus possesses valid `(raw_body, hmac)` pairs signed with the app's shared secret. That merchant can replay one of these bodies to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header value naming a victim shop. `HmacValidator.validate` only re-derives the HMAC from the (unchanged) body, so it still passes, and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop: [5](#0-4) 

The gem's own documentation instructs integrators to build the handler input directly this way, reinforcing that `request.shop` is expected to be trusted as the tenant boundary: [6](#0-5) 

This is the same root-cause pattern as the Plaza Finance report: a value that downstream logic treats as authoritative (there: reserve balance at claim time; here: the `shop` tenant identity) is not the value that was actually covered by the integrity/authorization check performed at the time of the action (there: fee accrual window; here: HMAC over body only).

### Impact Explanation
If the host application uses `request.shop`/`WebhookMetadata#shop` (exactly as the gem's own docs demonstrate) to key data updates, inventory sync, order processing, or entitlement changes per merchant, an attacker who is a legitimate merchant on the same app can forge webhook deliveries that are misattributed to a different shop. Since the shop identity is what separates one merchant's data from another's in a multi-tenant app, this is a cross-tenant access primitive: attacker-controlled data can be written into, or actions taken on behalf of, another tenant's account, achieved purely by replaying a body they legitimately received together with a modified header — no access token or secret theft required.

### Likelihood Explanation
Any account that can install the app (any merchant, i.e., an unprivileged internet user with respect to the app's other tenants) automatically obtains valid `(body, hmac)` pairs through ordinary webhook delivery for their own shop. Forging the header on a replayed POST requires no cryptographic material beyond what Shopify already sent them. The only prerequisite is that the host application uses the shop field from the processed webhook for tenant-scoped logic, which is exactly the pattern the gem's documentation recommends.

### Recommendation
Bind the tenant identity into the verified material instead of trusting an unsigned header:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` for `Webhooks::Request` (mirroring `AuthQuery`), if Shopify's signing scheme is extended to support that, or
- At minimum, document explicitly that `request.shop` is unauthenticated and that consuming applications must cross-check it against a known/installed shop list (session store) before trusting it for any tenant-scoped side effect, and update `docs/usage/webhooks.md` to demonstrate that check rather than showing bare `request.shop` usage.

### Proof of Concept
1. App is installed on `attacker.myshopify.com` and `victim.myshopify.com`, both using the same app `client_secret`.
2. Shopify delivers a legitimate webhook to the app for `attacker.myshopify.com`: raw body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker POSTs the same raw body `B` and the same `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only, matches `H`, and passes.
5. `Registry.process` invokes the handler with `WebhookMetadata#shop == "victim.myshopify.com"`, causing the application to process attacker-controlled data under the victim tenant's identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
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
