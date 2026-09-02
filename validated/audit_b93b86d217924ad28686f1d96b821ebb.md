### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body [1](#0-0) . The `shop` value that is then handed to the app's `WebhookHandler` as the authoritative tenant identifier for that event is read directly from an unauthenticated HTTP header and is never included in the signed payload [2](#0-1) . This breaks the identity binding: `hmac_valid(body) == true` does not imply `shop_header == shop_that_generated(body, hmac)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `HmacValidator.validate` computes/compares the signature strictly against that signable string using `Context.api_secret_key` [4](#0-3) . The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or the HMAC [5](#0-4) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant for the event, passing it into `WebhookMetadata` and on to the app-provided handler: [6](#0-5) . The documented usage pattern instructs integrators to use `data.shop` as the trusted shop identifier for enqueuing/processing work (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), reinforcing that this field is meant to be treated as authenticated [7](#0-6) .

For a multi-tenant (public) app, `Context.api_secret_key` is the same app-level secret used for every installed shop, so a valid `(body, hmac)` pair does not prove which shop it originated from — it only proves the pair was produced by something that knows the app secret. Because the shop header is excluded from what's signed, any actor who can obtain one genuine, validly-signed `(body, hmac)` pair (e.g., a webhook delivered to a delivery endpoint they control for their own installed shop) can replay that exact body/HMAC to the app's real webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still returns `true` (it never looks at the header), and `Registry.process` will dispatch the handler with `shop:` set to the attacker-chosen value — attributing the (attacker-controlled) event body to a completely different tenant.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem lets an app trust `shop` as if it were verified by the HMAC, when it is not. Depending on how the host application uses `data.shop` (e.g., looking up which shop's records to update/delete, enqueueing GDPR/mandatory redaction jobs, updating billing/subscription state, disabling features), an attacker can inject fabricated events attributed to a victim shop that they do not control and never authorized, without needing the app's `client_secret`, a stolen access token, or any privileged access to the victim's store — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitability depends on the attacker obtaining at least one genuine `(body, hmac)` pair without needing the secret directly — feasible in any app that lets a merchant configure/observe an HTTP delivery target for webhook subscriptions, or where webhook payloads otherwise reach an attacker-observable channel. It does not require possessing `api_secret_key`, an access token, or TLS interception. This is a design gap in the gem's `Request`/`HmacValidator`/`Registry` trust boundary rather than something requiring the host app to ignore documented behavior — the docs explicitly tell integrators to trust `data.shop`.

### Recommendation
Bind the shop identity to the signature verification step instead of trusting an unauthenticated header:
- Reject/flag mismatches where the topic/shop pairing cannot be corroborated against the registered webhook (e.g., cross-check `request.shop` against the session/shop the app expects for that specific webhook_id/topic combination), or
- At minimum, document/require that consumers must not treat `data.shop` as authenticated without additional server-side reconciliation (e.g., confirming the shop has a registered webhook with the given `webhook_id`), and consider incorporating `shop` into an application-level double-check (e.g., verifying `webhook_id` was actually registered for that shop before processing).

### Proof of Concept
1. App is a public/multi-tenant Shopify app; `Context.api_secret_key` is shared across all installed shops.
2. Attacker's own shop (`attacker.myshopify.com`) has the app installed and a webhook (e.g. `orders/create`) is configured to a delivery endpoint the attacker can inspect (or the attacker otherwise captures one legitimate delivery).
3. Attacker records the legitimate request: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
4. Attacker sends a new HTTP request to the app's real webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(api_secret_key, B) == H` [8](#0-7) .
6. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using `shop: "victim.myshopify.com"` and invokes the app's handler [9](#0-8) , causing the app to process attacker-controlled data as if it belongs to `victim.myshopify.com`.

### Citations

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
