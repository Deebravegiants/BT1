### Title
Webhook `shop` (and `topic`/`webhook_id`) header is trusted as verified but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before dispatching webhook data — including the `shop` field — to the app's handler. In reality, the HMAC signature computed by `Utils::HmacValidator` only covers the raw request body, never the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. Since a single app-level `api_secret_key` is used to sign webhooks for every shop that has installed the app, an attacker who controls a shop (e.g., their own dev/test store) can capture a validly-signed webhook body/HMAC pair from their own store's webhooks and replay it to the app's webhook endpoint while forging the `X-Shopify-Shop-Domain` header to name a victim shop. The HMAC check still passes because it never validated the shop binding, so the handler receives attacker-controlled body content labeled as belonging to the victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from attacker-controllable HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `to_signable_string` (i.e., the body), so it cannot detect a mismatched/forged `shop` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then forwards the unauthenticated `request.shop` (along with `topic`, `webhook_id`, `api_version`) straight into `WebhookMetadata` for the handler: [4](#0-3) 

The gem's own documentation reinforces that `process` is meant to fully verify the request's authenticity ("This will verify the request did indeed come from Shopify") and that `data.shop` is simply "The shop domain of the webhook" with no caveat that it is unauthenticated: [5](#0-4) [6](#0-5) 

This breaks the identity binding: `HMAC_valid(body) == true` is treated as equivalent to `shop_header == actual_originating_shop`, but the secret (`api_secret_key`) is shared across all shops installing the same app, and the signature never covers the shop claim. Any party that can obtain one valid `(body, hmac)` pair for the app (trivially available to an attacker who installs the app on their own store and triggers a webhook) can present that same pair with an arbitrary `shop` header and pass validation.

### Impact Explanation
This is a cross-tenant confusion vulnerability: an attacker can make the app process attacker-controlled webhook payload/topic data while it is attributed to a victim shop of the attacker's choosing. If the host app's handler uses `data.shop` to select which merchant's session/access token to act on (the documented, intended usage pattern per `docs/usage/webhooks.md`), the attacker can inject or trigger operations against a shop it does not control, using content it fully controls (attacker's own webhook body) — a cross-tenant access primitive satisfying the Critical impact bar.

### Likelihood Explanation
Likelihood is high for any attacker able to install the target app on a store they control (a normal, unprivileged path for many public apps) or otherwise obtain one legitimately signed webhook body/HMAC pair. No secrets, tokens, or privileged access are required — only the ability to send an arbitrary HTTP POST with attacker-chosen headers to the app's public webhook endpoint, which is exactly the interface `ShopifyAPI::Webhooks::Registry.process` is designed to receive.

### Recommendation
Bind the claimed `shop` (and ideally `topic`/`webhook_id`) to the HMAC verification instead of only signing/verifying the raw body — e.g., include the shop-domain header in the signable string, or otherwise cryptographically or out-of-band validate that the webhook's claimed shop matches an actively registered shop/webhook id for that specific delivery before dispatching to the handler. At minimum, update `docs/usage/webhooks.md` to explicitly document that `data.shop`, `data.topic`, `data.webhook_id`, and `data.api_version` are NOT covered by HMAC verification and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` header value `H` (valid because it's signed with the app's single, shared `api_secret_key`).
2. Attacker sends a POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id` optionally forged too.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only — matches `H` — validation passes.
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled content is processed as if it were authentic data for the victim shop.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
