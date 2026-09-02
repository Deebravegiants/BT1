### Title
Webhook `shop-domain` / `topic` headers are trusted for tenant identity without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as "verified" once the HMAC check passes, then hands the caller-supplied, HMAC-unprotected `shop` (and `topic`) header values to the app as trusted tenant identifiers, breaking the equality `shop authenticated by HMAC == shop used as the tenant key`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop`, `#topic`, `#webhook_id` are read directly from unauthenticated HTTP headers with no involvement in the signature computation [2](#0-1) . `HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (i.e. the raw body) and compares it to the `hmac-sha256` header [3](#0-2) . `Registry.process` raises only if this body-only HMAC fails, then immediately dispatches to the topic handler using `request.shop`, `request.topic`, and `request.webhook_id` as authenticated fields: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [4](#0-3) .

Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app (it is not per-shop), any merchant who installs the app can obtain a legitimately-signed webhook for their own store — i.e. a `(raw_body, hmac)` pair that passes `HmacValidator.validate`. Since the `shop-domain` and `topic` headers are not part of the signed material, that same valid `(body, hmac)` pair can be replayed to the same webhook endpoint with the `shopify-shop-domain` header rewritten to any other shop, or the `shopify-topic` header rewritten to any registered topic, and it will still pass validation. `Registry.process` will then call the app's handler with a `WebhookMetadata` whose `shop` claims to be a victim tenant while the `body` is fully attacker-controlled content originally issued for the attacker's own store.

Documentation for this API tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" [5](#0-4)  and shows a canonical handler that keys downstream business logic directly off `data.shop` (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [6](#0-5) . An app following this documented pattern exactly — with no host-side additional shop verification — inherits the tenant-confusion bug directly from the gem's own trust boundary, not from misuse of the API.

### Impact Explanation
This breaks tenant isolation: the equality that should hold is `shop value trusted by the handler == shop value cryptographically bound to the signed payload`, but the gem only binds the raw body, leaving `shop` (the tenant key) unauthenticated. A merchant of the app (an unprivileged actor with respect to other tenants) can forge webhook deliveries that the host app will process as belonging to a different shop, using their own legitimately-signed body. Depending on how the host app's handler acts on `data.shop` (session/store lookups, uninstall/redact processing, order/customer data ingestion), this enables cross-tenant data injection or state corruption keyed to a victim shop the attacker does not control — a cross-tenant access impact per the Critical impact category.

### Likelihood Explanation
Any developer building against the documented pattern is affected without any additional mistake on their part — the doc's own example uses `data.shop` as the trusted routing key [7](#0-6) . The only prerequisite is that the attacker be a legitimate installer of the target app (an unprivileged internet user relative to other tenants), able to trigger at least one real webhook for their own store and replay it with modified headers — no access token, `client_secret`, or privileged account is required.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signed material verified by `HmacValidator`, or otherwise cryptographically bind them to the payload before trusting them in `WebhookMetadata`. At minimum, document prominently that `shop`/`topic` on `WebhookMetadata` are not authenticated by the HMAC check and that host apps must independently verify the shop against an existing installed-shop/session record before acting on webhook content.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers for a topic (e.g. `orders/create`), receiving a legitimately Shopify-signed webhook: body `B`, header `shopify-hmac-sha256: H` (valid per `HmacValidator.validate` since `H = HMAC(secret, B)`), and `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays this exact `(B, H)` pair to the app's webhook endpoint, but rewrites `shopify-shop-domain` to `victim-shop.myshopify.com` (and/or `shopify-topic` to a different registered topic).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` and `Registry.process(request)` are called by the host app exactly as documented [8](#0-7) .
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(secret, B) == H` [9](#0-8) , which is unaffected by the header rewrite.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` [10](#0-9) , causing the app to process attacker-controlled data as if it originated from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L189-199)
```ruby
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** docs/usage/webhooks.md (L19-29)
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
