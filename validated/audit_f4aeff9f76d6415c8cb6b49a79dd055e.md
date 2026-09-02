### Title
Webhook `shop` identity is taken from an unauthenticated header while the HMAC only signs the body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity using `Utils::HmacValidator.validate(request)`, but the HMAC signable string is only the raw body [1](#0-0) . The `shop` value that is handed to the app's handler as the tenant identifier comes from the `X-Shopify-Shop-Domain` header, which is never part of the signed material [2](#0-1) .

### Finding Description
`Utils::HmacValidator.validate` computes an HMAC over `verifiable_query.to_signable_string` using the app's `Context.api_secret_key` and compares it to the `hmac` claim of the request [3](#0-2) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`; the `hmac`, `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled from HTTP headers that are excluded from what is signed [4](#0-3) .

`Registry.process` only checks the HMAC and then unconditionally trusts `request.shop` to build `WebhookMetadata`, which is passed straight to the app-supplied handler as the tenant identity for the payload: [5](#0-4) 

The binding that should hold is: `HMAC(secret, signed_bytes) valid ⇒ (body, shop) as delivered by Shopify`. What the code actually enforces is: `HMAC(secret, body) valid ⇒ body only`; `shop` is asserted, not verified, and is silently substitutable to any string by whoever controls the HTTP request headers.

Because the webhook signing secret (`api_secret_key`/`client_secret`) is the same for every shop that installs a given app, any shop that legitimately receives a validly-signed webhook (e.g., its own `orders/create` payload) can extract a `(raw_body, hmac)` pair that verifies successfully, then replay that exact body/hmac pair against the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a different, victim shop's domain. `HmacValidator.validate` will still return `true` because it never looks at the shop header, and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain [5](#0-4) .

### Impact Explanation
This lets one merchant/tenant attribute an arbitrary (but attacker-controlled, previously-observed) webhook payload to another tenant's shop domain from the perspective of the app's webhook handler — a cross-tenant data-integrity/spoofing issue rooted entirely in this gem's `Request`/`HmacValidator`/`Registry.process` trio, not in host-application misuse. The gem's own documentation instructs developers to rely on `Registry.process` to "verify the request did indeed come from Shopify" and then trusts `data.shop` as the tenant identity without any caveat that `shop` is unauthenticated [6](#0-5) [7](#0-6) . Any app that keys downstream logic (e.g., "which shop does this order belong to") off `data.shop`, exactly as the gem's own example handler does (`shop_domain: data.shop`) [8](#0-7) , is misled into believing the shop attribution has been cryptographically validated by `Registry.process`, when in fact only the body bytes were validated. This satisfies the "cross-tenant access" bar because the attacker (a legitimate but unprivileged installer of the app) can force the app to process/store data under a different tenant's identity without needing that tenant's credentials.

### Likelihood Explanation
Requires only: (1) being a shop that has installed the app (i.e., can receive real webhooks and thus harvest a valid `(body, hmac)` pair for the shared `api_secret_key`), and (2) the ability to send arbitrary HTTP requests with custom headers to the app's public webhook endpoint. No access token, TLS interception, or privileged account is needed — this is exactly an "unprivileged internet user" (any merchant that installs the target app) attack. This is a realistic, moderately likely scenario for any app relying on this gem's documented webhook flow.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`/`webhook_id`) into the HMAC-verified signable content, or require `Registry.process`/`HmacValidator` to independently corroborate the shop header against data already known to be authentic (e.g., cross-check against an active, previously-established session/shop record before trusting `WebhookMetadata#shop`), and update `docs/usage/webhooks.md` to explicitly warn that `shop` is not covered by the HMAC and must be revalidated by the host app before being trusted as a tenant identifier.

### Proof of Concept
1. App installs on `shop-a.myshopify.com` and `shop-b.myshopify.com` (attacker controls shop-a, victim is shop-b), sharing the same `api_secret_key`.
2. Shopify sends a legitimate webhook to the app's callback URL for `shop-a`:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: shop-a.myshopify.com
   Body: {"id":1,...}
   ```
3. Attacker (who received this webhook, e.g. by exposing/logging it) replays the identical body and HMAC header to the same endpoint, only changing:
   ```
   X-Shopify-Shop-Domain: shop-b.myshopify.com
   ```
4. `Utils::HmacValidator.validate` recomputes `HMAC(secret, raw_body)` — unchanged from step 2 — and passes [9](#0-8) .
5. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(..., shop: "shop-b.myshopify.com", ...))`, attributing shop-a's order payload to shop-b [5](#0-4) .

Note: I could not verify from the indexed files whether any downstream Shopify-maintained middleware (outside this gem, e.g. `shopify_app`) adds an additional shop-authenticity check on top of `Registry.process`; my analysis is scoped strictly to `lib/shopify_api/webhooks/**` and `lib/shopify_api/utils/hmac_validator.rb` as indexed.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
