### Title
Webhook `shop` (and `topic`) identity fields are not covered by HMAC verification, allowing shop-domain spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally forwards `request.shop` to the app's handler as the identity of the shop that sent the webhook, even though that value was never part of what the HMAC actually signs.

### Finding Description
`Registry.process` performs exactly one authenticity check before dispatching to the merchant's webhook handler: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`; `shop`, `topic`, `webhook_id`, and `api_version` are all read from headers and are never mixed into the signed bytes: [3](#0-2) 

This creates the identity-binding break the report's bug class describes: **the field acted on (`request.shop`, forwarded to the handler and typically used to look up/act on that shop's data or session) is not the field covered by the HMAC** (only `@raw_body` is signed). Formally: `shop_verified_by_hmac ⊄ shop_used_by_handler`.

The library's own documentation promises stronger guarantees than are actually delivered: it states that calling `Registry.process` "will verify the request did indeed come from Shopify" and then instructs handlers to trust `data.shop` as "The shop domain of the webhook": [4](#0-3) [5](#0-4) 

Because the header value is not bound to the signature, an unprivileged attacker who has legitimately received one authentic webhook delivery (e.g. by installing the app on their own store and triggering a webhook event, which is a normal, unprivileged interaction — no `api_secret_key`, access token, or leaked credential required) can replay the exact same body + `hmac-sha256` header to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header. `HmacValidator.validate` still passes, because it never inspected those headers, and `Registry.process` calls the handler with the attacker-chosen `shop` value.

### Impact Explanation
This crosses a tenant boundary using only the attacker's own legitimately-issued webhook material: the app processes/attributes webhook data as belonging to a victim shop chosen by the attacker, even though the HMAC only proves the body originated from the attacker's own store. Depending on how the host app's handler uses `data.shop` (e.g. session lookup, per-shop data writes, billing/order state changes), this enables cross-tenant data confusion or forged events "from" a shop the attacker does not control — the analog of a shop-authentication bypass caused purely by the gem's own signature scope, not by host-app misuse of a documented safeguard (the docs actively claim the whole request is verified).

### Likelihood Explanation
Likelihood is realistic but not trivial: the attacker must control at least one shop with the target app installed (a normal, low-privilege merchant action) to obtain one authentic `(raw_body, hmac)` pair, and the app's webhook endpoint must be reachable from the internet (true by design for HTTP webhooks). No secrets, tokens, or privileged access are required beyond that.

### Recommendation
Bind the identity fields to the signature verification path rather than trusting bare headers: either (a) require/verify that `shop` (and `topic`/`webhook_id`) match a shop for which the app currently holds an active session/installation before invoking the handler, or (b) clearly document in `docs/usage/webhooks.md` that `HmacValidator.validate` only authenticates the request body and that handlers must independently authenticate `data.shop` against their own store of installed shops before acting on it, rather than stating the request itself "did indeed come from Shopify."

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the POST body `B` and the `x-shopify-hmac-sha256` header value `H` sent to the app's public webhook endpoint (`H` is a valid HMAC of `B` under the app's shared `api_secret_key`).
2. Attacker resends a new HTTP request to the same webhook endpoint with:
   - body = `B` (unchanged)
   - `x-shopify-hmac-sha256` = `H` (unchanged)
   - `x-shopify-shop-domain` = `victim-shop.myshopify.com` (attacker-controlled)
   - `x-shopify-topic` unchanged or altered similarly
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully (headers only checked for presence, not content), and `HmacValidator.validate` succeeds because it only recomputes the HMAC over `B`, per `to_signable_string`.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-supplied data as if it came from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
