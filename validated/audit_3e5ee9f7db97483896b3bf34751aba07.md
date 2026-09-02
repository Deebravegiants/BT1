Confirmed: `WebhookMetadata.shop` (docs/usage/webhooks.md:14, lib/shopify_api/webhooks/webhook_handler.rb:6-8) is documented as "the shop domain of the webhook" and host apps are told to key their tenant logic off it, while the value is populated straight from `request.shop` — an unauthenticated header — and never included in the HMAC input. [1](#0-0) [2](#0-1) 

### Title
Webhook `shop` field is not covered by HMAC, allowing cross-tenant webhook spoofing via header/body mismatch - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` computes/compares the HMAC exclusively over that body against the `x-shopify-hmac-sha256` header. Neither the `x-shopify-shop-domain` header nor the `x-shopify-topic`/`x-shopify-webhook-id` headers are part of the signed material. `Registry.process` nonetheless treats `request.shop` (read straight from the unauthenticated header) as trusted tenant identity and passes it into `WebhookMetadata`, which host applications are documented to use to route/associate incoming webhook payloads to a specific merchant. [3](#0-2) [4](#0-3) [5](#0-4) 

### Finding Description
The identity binding this gem is supposed to guarantee is: `shop header used to attribute the webhook == shop that Shopify's HMAC signature actually authenticates`. Because `to_signable_string` only returns `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`), and `HmacValidator#validate_signature` computes `OpenSSL::HMAC.hexdigest` over that same signable string with the app's single `Context.api_secret_key` (`lib/shopify_api/utils/hmac_validator.rb:26-31`), a signature that is valid for one shop's webhook body is equally valid for *any* request carrying that same body and any attacker-chosen `x-shopify-shop-domain`/`shopify-shop-domain` header, since the app's `client_secret` is identical for every shop that has the app installed.

`Registry.process` performs no additional binding check — it validates HMAC, looks up the handler by `request.topic`, and calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` (`lib/shopify_api/webhooks/registry.rb:188-200`). The `shop` value handed to the host application's handler is thus fully attacker-controllable while the HMAC only vouches for the body bytes.

### Impact Explanation
An attacker who controls a shop with the app installed (a normal, unprivileged install any developer/merchant can obtain) can capture one of their own legitimate webhook deliveries — valid raw body + valid HMAC signed by Shopify using the app's shared `client_secret` — and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. The gem's `HmacValidator.validate` still returns `true` because the signable string (raw body only) is untouched, so `Registry.process` proceeds and calls the host handler with `WebhookMetadata#shop` set to the victim's domain. Any host application that uses `data.shop` (as the docs instruct, `docs/usage/webhooks.md:26`) to select which merchant's records to update, credit, or overwrite is left processing attacker-authored data under a foreign tenant's identity — a cross-tenant data-integrity/confidentiality breach that maps to the report's core bug class ("field acted on but not covered by the HMAC").

### Likelihood Explanation
Likelihood is high in relative terms: no special credentials beyond a normal app install are required, capturing one's own webhook payload/HMAC pair is trivial (dev store, ngrok, request logging), and the header can be freely modified on replay since HTTP headers are not part of the TLS/HMAC-protected content this gem checks. The only constraint is that the victim's shop must be reachable via the same registered webhook path and topic, which is the common case for multi-tenant apps using this gem's `Registry`.

### Recommendation
Bind the shop identity into the material that is actually verified: either (a) require callers to pass the expected/session shop alongside the request and compare it against `request.shop` before invoking the handler, cross-checked against the shop stored for the currently active offline session/topic subscription, or (b) reconstruct the signable string from a canonical representation that includes `topic`, `shop-domain`, and `webhook_id`, not just the raw body, so that tampering with those headers invalidates the HMAC. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be revalidated by the host app (e.g., against a known list of installed shop domains) before being trusted for tenant routing.

### Proof of Concept
1. App `X` is installed on attacker's own shop `attacker.myshopify.com` and on victim `victim.myshopify.com`, both sharing the same app `client_secret`.
2. Shopify sends a legitimate webhook to app `X` for `attacker.myshopify.com`:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`
   - Body: `{"id": 1, "note": "attacker-controlled content"}`
3. Attacker replays the exact same body and HMAC header, but swaps `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged header into `request.shop == "victim.myshopify.com"` (`lib/shopify_api/webhooks/request.rb:20-23`).
5. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashed `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
6. The host app's `WebhookHandler#handle` receives `data.shop == "victim.myshopify.com"` with attacker-authored `data.body`, and — following the documented usage pattern (`docs/usage/webhooks.md:26`) — applies it to the victim's tenant data.

### Citations

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
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
