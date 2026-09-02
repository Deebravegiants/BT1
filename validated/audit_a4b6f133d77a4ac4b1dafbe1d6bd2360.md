### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated headers while only the request body is covered by the HMAC - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by verifying only the HMAC over the raw request body, then passes the `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — to the app's handler as if they were verified. This breaks the identity binding: `shop-domain header used by handler != shop-domain covered by HMAC`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from HTTP headers, none of which participate in `to_signable_string`: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then forwards the header-derived `shop` (and other header fields) straight to the app's `WebhookHandler`, treating them as authenticated: [3](#0-2) 

The gem's own documentation explicitly tells developers that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` can be trusted to route/act on behalf of a specific shop: [4](#0-3) [5](#0-4) 

Because the HMAC only covers the body, any request whose body+HMAC pair is valid for *some* shop (e.g. a shop the attacker legitimately installed the app on, which will receive real Shopify-signed webhooks with a valid HMAC over that body) can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header swapped to a victim shop's domain. `HmacValidator.validate` will still succeed because it never inspects the shop header — it recomputes the signature purely from `@raw_body`: [6](#0-5) 

This is the exact bug class from the reference report generalized: a field that is acted on (`shop`, used by the handler as the tenant identity) is not covered by the cryptographic check (`_validateSwap`/HMAC) that is supposed to gate the operation.

### Impact Explanation
An unprivileged internet user who controls (or has installed the app on) any single shop can forge webhook deliveries that the app will process as belonging to an arbitrary victim shop domain, because `shop` is not bound to the HMAC. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to select a stored session/access token, to trigger mandatory `shop/redact`, `customers/redact`, `customers/data_request` handling, or other per-tenant side effects), this enables cross-tenant action: the attacker's own webhook body content gets processed under a different shop's identity, e.g. triggering data-redaction or shop-lifecycle logic against a shop the attacker does not own/control. This matches the "Critical — cross-tenant access" impact bucket.

### Likelihood Explanation
Requires only: (1) the attacker runs the app on their own shop and captures a legitimate `(raw_body, hmac)` pair from a real Shopify webhook delivery (trivial, since installing any Shopify app and receiving one webhook suffices), and (2) the ability to POST arbitrary headers to the app's public webhook endpoint (standard for any internet-reachable webhook route documented by this gem). No access token, `api_secret_key`, or privileged access is needed — only knowledge of the gem's documented `process` usage pattern shown in `docs/usage/webhooks.md`.

### Recommendation
Bind the identity fields into the HMAC-verified payload rather than trusting raw headers post-hoc: e.g., include `shop-domain`, `topic`, and `webhook-id` in the value that is HMAC-verified (Shopify signs the body only, so this requires the app/gem to independently cross-check the header-provided `shop` against a value known to be tied to that specific delivery — for instance by requiring that the shop have an active, registered webhook subscription for that specific `webhook_id`/topic, or by rejecting deliveries where `shop` does not match a shop the app can independently corroborate). At minimum, document prominently that `Registry.process`'s HMAC check does **not** authenticate the `shop`, `topic`, `webhook_id`, or `api_version` headers, so host applications must not treat `WebhookMetadata#shop` as an authenticated tenant identifier without additional verification (e.g. correlating against `webhook_id` uniqueness per registered shop).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers for a webhook topic (e.g. `orders/create`).
2. Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC over `B` using the app's `api_secret_key`), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the same `B`/`H` to the app's public webhook route, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-hmac-sha256" => H})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only rehashes `B` — see `lib/shopify_api/utils/hmac_validator.rb:12-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled content under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
