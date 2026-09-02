This confirms the finding: the docs explicitly document that `data.shop` (the shop domain) is derived from the webhook header and passed straight to the handler, and `Registry.process` states it will "verify the request did indeed come from Shopify" via `Utils::HmacValidator.validate(request)` — but that HMAC only covers `to_signable_string` (the raw body), never the `shop-domain` header.This confirms the full picture. `Webhooks::Request` extracts `shop` (line 21-23 of `lib/shopify_api/webhooks/request.rb`) purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, and `to_signable_string` (used by `HmacValidator.validate`) only returns `@raw_body` — the `shop` header is never part of the signed bytes. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) trusts `request.shop` and hands it straight into `WebhookMetadata`, which the host app's handler uses as the tenant identifier for the webhook, exactly matching the documented usage pattern in `docs/usage/webhooks.md:125` ("This will verify the request did indeed come from Shopify").

### Title
Webhook `shop` identity is not bound to the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, while `HmacValidator.validate` only verifies the HMAC over `to_signable_string`, which is the raw body alone. Since the app's `client_secret` (`Context.api_secret_key`) is identical for every shop that installs the same app, any unprivileged internet user who installs the app on their own (e.g., free/dev) store can capture a genuinely-signed webhook `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. `HmacValidator.validate` still returns `true` because the signed bytes (`raw_body`) are unchanged, and `Registry.process` will dispatch the forged data to the handler tagged with the victim's shop, breaking the identity binding "shop authenticated == shop acted upon."

### Finding Description
- `lib/shopify_api/webhooks/request.rb:20-23`: `shop` is taken from `shopify_header("shop-domain")`, entirely attacker-controlled input on the wire, with no cryptographic tie to the payload.
- `lib/shopify_api/webhooks/request.rb:35-38`: `to_signable_string` returns only `@raw_body`; `topic`, `shop`, `webhook_id`, and `api_version` headers are excluded from what gets signed/verified.
- `lib/shopify_api/utils/hmac_validator.rb:26-31`: `validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received signature — i.e., it authenticates the body bytes only.
- `lib/shopify_api/webhooks/registry.rb:188-199`: `process` calls `Utils::HmacValidator.validate(request)`, and on success immediately builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` and invokes the developer's `handler.handle`, using the unauthenticated `shop` header as the tenant identity passed to app logic.
- `docs/usage/webhooks.md:123-125` documents this exact call path as verifying "the request did indeed come from Shopify," reinforcing that host apps are expected to trust `data.shop` as authenticated once `Registry.process` succeeds.

Because the same `client_secret` is shared across all shops that install a given app, any attacker can install the app on a shop they control, receive a legitimately HMAC-signed webhook for their own shop, and then POST that identical `raw_body`/HMAC pair to the victim's app instance while substituting the `shop-domain` header for the victim's `myshopify.com` domain. `Registry.process` cannot distinguish this from a genuine webhook for the victim shop, since the shop field it trusts was never covered by the signature.

### Impact Explanation
This is a cross-tenant identity binding failure: the equality the gem should enforce is `shop authenticated (by HMAC) == shop acted upon (by handler)`, but the header-derived `shop` is disjoint from the HMAC-verified content. An attacker can cause the host application to process attacker-supplied webhook bodies (topic, payload) under an arbitrary victim shop's identity — e.g., triggering `orders/create`, `app/uninstalled`, `shop/redact`, or `customers/data_request` handling logic for a shop the attacker doesn't operate, potentially causing the app to delete/redact victim data, desynchronize inventory/order state, or otherwise act on the victim tenant based on attacker-forged content. This matches the "cross-tenant access" criterion.

### Likelihood Explanation
Reachable by any unprivileged internet user: webhook HTTP endpoints are public by design (Shopify posts to them over the internet), and obtaining one genuine `(body, hmac)` pair only requires installing the target app on an attacker-owned shop (trivial with a free Shopify developer/partner store) — no leaked credentials, no access to `api_secret_key`, and no social engineering required. The replay itself is a single crafted HTTP POST with a modified header.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the same authenticated channel as the body, or otherwise cryptographically tie the header values to the signed content, e.g.:
- Include the `shop-domain` (and `topic`) header value in the string that is HMAC-verified (`to_signable_string`), matching what is actually authenticated to what is acted upon; or
- Require host applications to independently confirm `request.shop` corresponds to a shop with an active, previously-established session/installation record before trusting `WebhookMetadata#shop`, and document this requirement prominently next to the "this will verify the request did indeed come from Shopify" claim in `docs/usage/webhooks.md`, since today's wording implies full authentication of all fields including `shop`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop the attacker fully controls) and receives a genuine webhook, e.g. for `orders/create`, with body `raw_body` and header `x-shopify-hmac-sha256: <valid_hmac>` computed with the app's real `client_secret`.
2. Attacker replays the exact same request to the app's public webhook endpoint, only changing `x-shopify-shop-domain` from `attacker-shop.myshopify.com` to `victim-shop.myshopify.com`.
3. Server-side: `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged header; `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — unchanged — and returns `true`.
4. `Registry.process` builds `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)` and invokes the host app's `handler.handle`, which now performs its logic (e.g., recording an order, redacting data, deregistering) against `victim-shop.myshopify.com` using attacker-controlled body content, despite the victim never having sent this webhook. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
