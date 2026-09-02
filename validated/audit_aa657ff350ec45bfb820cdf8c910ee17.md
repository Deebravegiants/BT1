Based on my analysis, I found a valid analog in the webhook processing path: the HMAC signature only binds the raw request body, while the `shop` and `topic` fields — which are used to route/attribute the event to a specific tenant — travel unauthenticated in headers.

### Title
Webhook shop and topic identity not bound by HMAC, enabling cross-tenant event spoofing after signature validation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed by an entity possessing `Context.api_secret_key` [2](#0-1) . The `shop`, `topic`, `webhook-id`, and `api-version` values are read directly from HTTP headers and are never part of the signed string [3](#0-2) . `Registry.process` nonetheless uses these unauthenticated header values as the tenant/topic identity dispatched to the app's handler once the (body-only) HMAC check passes [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop header == shop that the signed bytes originated from`. Because `to_signable_string` excludes `shop`, `topic`, and `webhook-id`, this equality is never checked — only `HMAC(body, secret)` is checked. `Context.api_secret_key` is the app's single `client_secret`, shared across every merchant/shop that has installed the app; it is not a per-shop key. Consequently, any raw body/HMAC pair that is valid for one shop is *also* a cryptographically valid pair for every other shop the same app serves, because the signature carries no shop-scoped information at all.

An actor who legitimately controls one shop that has the app installed (an "unprivileged" tenant relative to other merchants of the same app) can capture a genuine webhook delivery for their own store — a valid `(raw_body, hmac)` pair. They can then replay that exact body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` and/or `x-shopify-topic` headers for a different, victim shop/topic. `HmacValidator.validate` will report success because the body is untouched and the HMAC still matches [5](#0-4) , and `Registry.process` will hand the handler a `WebhookMetadata`-equivalent payload whose `shop`/`topic` come straight from the attacker-controlled headers [6](#0-5) .

### Impact Explanation
Applications built on this gem's documented webhook API (see `docs/usage/webhooks.md`, which instructs to construct `Request` from raw headers and pass it straight to `Registry.process`) [7](#0-6)  rely on `request.shop`/`request.topic` as trusted tenant identifiers once `process` doesn't raise. Since these values are unauthenticated, a webhook payload can be attributed to, and processed as belonging to, an arbitrary victim shop — i.e., cross-tenant event injection/spoofing, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be able to trigger and observe one legitimate webhook delivery for a shop they control (any shop can install most public apps) and then send their own HTTP POST to the app's public webhook endpoint with modified headers — no `client_secret`, access token, or privileged access is required. This fits the "unprivileged internet user" threat model.

### Recommendation
Include `shop-domain` (and ideally `topic`) inside the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., verify `request.shop` against the shop associated with the currently active/expected session before dispatching to the handler), mirroring the fix pattern for the re-org report: "every operation needs to include the key parameters it claims to act on" as part of the identity check, not just an unrelated body signature.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com`, which has the target app installed; app has one global `client_secret`.
2. Shopify sends a legitimate webhook to the app for `attacker-shop`: `raw_body = '{"id":1}'`, headers include `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid_hmac_of_body>`.
3. Attacker captures this body/HMAC pair (e.g., by owning the shop and observing their own webhook logs/proxy).
4. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` to the same webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`).
5. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `to_signable_string` is still `raw_body` [1](#0-0) ; `Utils::HmacValidator.validate` succeeds because the HMAC only ever certified the body [2](#0-1) .
6. `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content [8](#0-7) , causing the app to act on forged data as if it originated from the victim tenant.

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
