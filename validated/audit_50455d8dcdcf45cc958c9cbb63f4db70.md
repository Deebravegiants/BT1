### Title
Webhook shop/topic attribution not covered by HMAC signature enables cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` only proves that the *body* was signed with the app's `api_secret_key`. The `shop`, `topic`, `webhook_id`, and `api_version` fields — read straight from HTTP headers and never covered by the HMAC — are the exact fields `Registry.process` uses to route to a handler and attribute the payload to a tenant.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

Only `@raw_body` is signed. `shop`, `topic`, `webhook_id`, and `api_version` all come from `shopify_header`, i.e. plain, unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then uses the unverified `topic` header to select a handler and forwards the unverified `shop` header to the app's business logic: [3](#0-2) 

The `HmacValidator` itself computes/compares the signature purely over `to_signable_string` (the raw body), with no binding to any header value: [4](#0-3) 

The documented integration pattern feeds `request.headers.to_h` straight from the HTTP layer into `Request.new`, with no additional binding performed by the host app either: [5](#0-4) 

**Equality that should hold but doesn't:** `shop header value == shop the HMAC-signed body was generated for`. The HMAC only proves `body == HMAC⁻¹(api_secret_key, signature)`; it proves nothing about the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, or `X-Shopify-Api-Version` headers that accompany it.

### Impact Explanation
Because `api_secret_key` is shared across every shop/tenant that installs the app, any tenant that legitimately receives a signed webhook (a valid, unprivileged, but untrusted party from the perspective of *other* tenants) can capture that request and replay it to the same endpoint with the `X-Shopify-Shop-Domain` header rewritten to a different shop, and/or the `X-Shopify-Topic`/`X-Shopify-Webhook-Id` headers changed — the body-only HMAC remains valid. `Registry.process` will still pass `Utils::HmacValidator.validate`, route based on the attacker-chosen topic, and hand the handler a `WebhookMetadata` claiming an arbitrary `shop` value. Any host application that uses `data.shop` (as the documented example does — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) to select which tenant's records to write to will process another tenant's data under the attacker-chosen shop identity — a cross-tenant integrity violation stemming entirely from this gem's verification primitive.

### Likelihood Explanation
Likelihood is constrained by the fact that the attacker must already be a legitimate installer of the app (to receive a validly-signed webhook body in the first place) and by the app needing to trust `data.shop`/`data.topic` for tenant-scoped actions, which the gem's own documentation encourages. No secrets, TLS interception, or privileged accounts are required — only capturing/replaying a webhook HTTP request with modified headers, which any unprivileged party who installs the app can do repeatedly against their own known endpoint.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the signable content (e.g., include them, canonically encoded, alongside the body before computing/verifying the HMAC), or have `Registry.process` independently re-derive/verify these values against session/store state rather than trusting unauthenticated headers. At minimum, document prominently that these header-derived fields are not authenticated by `HmacValidator` and must not be used for tenant-scoping decisions without independent verification (e.g., checking the shop against an existing installed-shop record).

### Proof of Concept
1. Attacker installs the app for `attacker-shop.myshopify.com` and registers a webhook, receiving a legitimately Shopify-signed request:
```
POST /callback/orders/create
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <valid HMAC of body B>
X-Shopify-Shop-Domain: attacker-shop.myshopify.com
X-Shopify-Webhook-Id: w1
X-Shopify-Api-Version: 2024-01
Body: B
```
2. Attacker replays the identical body `B` (same bytes, same valid HMAC) to the same endpoint but rewrites the header:
```
X-Shopify-Shop-Domain: victim-shop.myshopify.com
```
3. `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: tampered_headers))` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` — it still matches — so validation passes: [3](#0-2) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, and any host app logic keyed on `data.shop` (per the documented example) now attributes/acts on the payload as belonging to `victim-shop`, despite the payload actually originating from and describing `attacker-shop`.

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
