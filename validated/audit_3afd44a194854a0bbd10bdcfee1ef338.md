### Title
Webhook `shop` identity is not covered by the HMAC, allowing cross-tenant shop-domain spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before invoking the app's handler with a `WebhookMetadata` object whose `shop` field the docs describe as trustworthy ("The shop domain of the webhook"). In reality, the HMAC signature only authenticates the raw request body; the `shop` value passed to the handler is read from an unauthenticated header and is never bound to the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, however, is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside of the signed bytes: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string` (i.e. the body) and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` validates only that HMAC, then immediately forwards `request.shop` (the unauthenticated header value) to the handler as authenticated data: [4](#0-3) 

The identity binding broken here is:
`hmac_valid(raw_body) == true` is treated as equivalent to `shop_header == authenticated_shop`, when in fact these are independent values. The bytes that are cryptographically verified (`raw_body`) are not the bytes that are parsed and trusted as tenant identity (`shop` header).

The `api_secret_key` used to compute this HMAC is the app's single client secret shared across every merchant that installs the app — it is not shop-specific. Therefore, any merchant who legitimately installs the app can capture a genuinely-signed webhook body+HMAC pair from their own shop (a valid `(body, hmac)` pair under the app's secret) and replay that exact body and HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass (it never inspects headers), and `Registry.process` will call the handler with `WebhookMetadata.shop` equal to the attacker-chosen victim domain.

This does not depend on the host app misusing the gem: the gem's own documentation instructs developers to use `data.shop` directly (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`), and to rely on `Registry.process` for authenticity: [5](#0-4) [6](#0-5) 

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery. An attacker who is a legitimate installer of the app (their own tenant) can forge webhook deliveries that appear — per the gem's documented contract — to be authenticated events from a different tenant (victim shop), since `Registry.process`'s success is documented as proof that "the request did indeed come from Shopify" for that shop. Downstream apps following the documented pattern will process/store/act on data keyed by the attacker-controlled `shop` value, resulting in cross-tenant data injection or state corruption attributed to a victim shop the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker be able to legitimately install the target app on their own store (a standard, unprivileged step for any Shopify merchant/attacker) and control an HTTP client capable of sending a crafted request to the app's public webhook endpoint with custom headers. No possession of `api_secret_key`, access tokens, or TLS interception is needed — only a body+HMAC pair the attacker legitimately received for their own tenant.

### Recommendation
Bind the `shop` (and ideally `topic`, `api_version`, `webhook_id`) to the authenticated bytes, e.g. include the relevant Shopify headers in the HMAC-signable string, or independently verify that `request.shop` corresponds to a shop with an active, previously-established session/installation record before dispatching to the handler. At minimum, update the documentation to explicitly warn that `data.shop` is not authenticated by the HMAC check and must be cross-checked against known installed shops by the host application.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers/receives an http webhook, e.g. for `orders/create`.
2. Attacker captures the raw POST body `B` and the header `x-shopify-hmac-sha256: H` from this legitimately-delivered webhook (`H = HMAC-SHA256(app_secret, B)`, valid since the app secret is shared across tenants).
3. Attacker sends a new POST request to the app's public webhook endpoint with:
   - Body: same `B`
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid for body `B`)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (attacker-substituted)
   - Header `x-shopify-topic: orders/create`
4. `ShopifyAPI::Webhooks::Request.new` parses these headers; `HmacValidator.validate` recomputes `HMAC-SHA256(app_secret, B)` and it matches `H` — validation passes.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`.
6. The host app, following the gem's documented pattern (`data.shop`), processes/persists this data as if it were an authenticated event from `victim-shop.myshopify.com`, even though `victim-shop.myshopify.com` never sent or authorized this webhook.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L19-30)
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
```

**File:** docs/usage/webhooks.md (L123-130)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
```
