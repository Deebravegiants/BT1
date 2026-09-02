### Title
Webhook Shop-Domain Header Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` computes the HMAC-verified payload from `@raw_body` only [1](#0-0) , while the `shop`, `topic`, and `webhook_id` values consumed by `Registry.process` are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the body HMAC and then dispatches the handler using these header-derived, unsigned identity fields [3](#0-2) .

### Finding Description
The intended binding is: `verified_bytes == bytes_the_handler_acts_on_for_identity`. In `HmacValidator.validate`, `verifiable_query.to_signable_string` is HMAC'd against `Context.api_secret_key` [4](#0-3) . For webhooks, `to_signable_string` returns only the raw body [1](#0-0) . The `shop` (`x-shopify-shop-domain`), `topic`, `webhook_id`, and `api_version` fields are pulled straight from `@headers`, which are never part of the signed bytes [5](#0-4) .

`Registry.process` raises only if the body HMAC fails, then immediately builds `WebhookMetadata` using `request.shop` and `request.topic` from headers and hands it to the app's registered handler [3](#0-2) . The gem's own documentation instructs apps to trust these fields directly: `data.shop` is described as "The shop domain of the webhook" and is passed straight into app logic without any further verification requirement documented [6](#0-5) .

Because the same app-level `api_secret_key` is shared across every shop that installs the app, any merchant who legitimately installs the app receives real webhooks with a valid HMAC over the raw body. Since the header values (`shop`, `topic`, `webhook_id`) are never covered by that HMAC, that same attacker-controlled merchant can replay the identical `raw_body` + `hmac` value while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header for a different tenant's shop domain. `Utils::HmacValidator.validate` will still return `true` — it never inspects headers — and `Registry.process` will invoke the handler believing the event legitimately originated from the victim shop.

This breaks the intended equality: `shop_the_HMAC_was_computed_for == shop_the_handler_believes_sent_the_event`. The gem provides no field or documented mechanism binding the header-derived tenant identity to the signed bytes, so any application that keys per-tenant state (access tokens, order records, side effects) off `WebhookMetadata#shop` inherits a cross-tenant confusion vector purely from this gem's verification logic.

### Impact Explanation
This satisfies the Critical bar of "cross-tenant access": an attacker with their own legitimate, unprivileged installation of a multi-tenant app can craft webhook deliveries whose signature validates successfully but whose declared `shop` is an arbitrary victim tenant. Any app that looks up a session/access token keyed by `WebhookMetadata#shop` and performs actions against Shopify (or its own DB) using the attacker-supplied body under the victim's identity is exposed to cross-tenant data corruption or unauthorized actions attributed to a shop the attacker does not control — all without ever needing the victim's credentials, access token, or `client_secret`.

### Likelihood Explanation
Likelihood is high for any app that (a) is multi-tenant, (b) allows public/self-serve installation (so the attacker can install it on their own store to obtain a validly-signed webhook), and (c) trusts `WebhookMetadata#shop` from `Registry.process` as the tenant identity without independently confirming it against the shop that owns the specific `webhook_id`/subscription. The gem's documented flow (`docs/usage/webhooks.md`) does not instruct apps to perform such additional confirmation, and the `Request`/`Registry` API design makes the header values look validated once `process` returns without error.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the material that is verified — either by having Shopify's HMAC computation cover them (not possible unilaterally, since Shopify controls the signing on their side) or, more practically within this gem, by requiring/encouraging verification of `shop` against the specific webhook subscription record (keyed by `webhook_id`) that the app itself created via `Registry.register`, rather than trusting the header value as ground truth. At minimum, update `docs/usage/webhooks.md` to explicitly warn that `data.shop`/`data.topic` are not covered by the HMAC and must be cross-checked against the app's own webhook registration records before being used for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the multi-tenant app on their own shop `attacker.myshopify.com`, receiving legitimate webhooks (e.g. `orders/create`) with header `x-shopify-shop-domain: attacker.myshopify.com`, some `raw_body`, and a valid `x-shopify-hmac-sha256` computed by Shopify over that `raw_body` using the app's shared `client_secret`.
2. Attacker captures this raw HTTP request unmodified except for changing `x-shopify-shop-domain` to `victim.myshopify.com` (and optionally the `webhook_id`), sends it to the app's webhook endpoint.
3. App calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body:, headers:))` [7](#0-6) .
4. `Utils::HmacValidator.validate(request)` succeeds because it only recomputes the HMAC over `@raw_body`, which is unchanged [1](#0-0) [4](#0-3) .
5. The app's handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: attacker_controlled, ...)` [8](#0-7)  and performs tenant-scoped actions against `victim.myshopify.com` using attacker-supplied data.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L128-135)
```markdown
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
