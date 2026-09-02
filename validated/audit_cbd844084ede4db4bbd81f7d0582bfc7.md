### Title
Webhook shop-domain is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating only the raw HTTP body against the `x-shopify-hmac-sha256` header, but the `shop` value that is handed to the app's handler (and used to key per-tenant data) comes from the unauthenticated `x-shopify-shop-domain` header. The binding "shop the HMAC was computed for" == "shop the handler is told to act on" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside the signed material: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` and then dispatches `request.shop` straight into `WebhookMetadata`, which is the only tenant identifier passed to the app's handler: [4](#0-3) 

`HmacValidator.validate` only calls `verifiable_query.to_signable_string`, so for a `Request` object it only ever HMACs the body — the shop header plays no part in the equality check: [5](#0-4) 

`WebhookMetadata.shop` is a plain `const :shop, String` with no further validation, and is exactly what host apps are documented to use to route/attribute webhook data to a specific merchant: [6](#0-5) 

Contrast this with the OAuth path in the same gem, where `Auth::Oauth::AuthQuery#to_signable_string` explicitly folds `shop` into the signed parameter set, so `shop` cannot be swapped without invalidating the HMAC: [7](#0-6) 

This shows the gem is capable of, and elsewhere does, bind `shop` into the HMAC — the webhook path simply omits it. The equality that should hold is:
`shop authenticated by HMAC` == `shop delivered to WebhookHandler#handle`
but because `to_signable_string` for `Request` never includes `shop`, the actual invariant enforced is only `body authenticated by HMAC` == `body delivered`, with `shop` free to be anything the sender puts in the header.

### Impact Explanation
Any unprivileged internet user who can obtain one genuine `(raw_body, hmac)` pair — e.g., by installing the target app on their own development/test store and capturing a real webhook Shopify sends them — can replay that exact body and signature to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `Registry.process` will pass HMAC validation (since only the body is checked) and hand the handler a `WebhookMetadata` whose `shop` field names a victim merchant chosen by the attacker. For multi-tenant apps that use `data.shop` to select which merchant's records to update/create/delete (the documented and expected usage pattern shown in `docs/usage/webhooks.md` and mirrored in the test suite), this is a cross-tenant data integrity/confidentiality break: an attacker can inject fabricated "events" attributed to a shop they do not own and do not have credentials for. This matches the required "cross-tenant access" impact class since no access token, `client_secret`, or privileged account is needed — only a body/signature pair the attacker legitimately received for their own store.

### Likelihood Explanation
Likelihood is high for any app that (a) is installed on more than one shop and (b) trusts `WebhookMetadata#shop` from `Registry.process` as the tenant key, which is the intended and documented usage of this API. The attacker needs no secret material from the victim; they only need their own (attacker-owned) store's webhook body+signature, both of which are delivered to them legitimately by Shopify. The webhook endpoint is by definition internet-reachable and unauthenticated aside from the HMAC check this gem performs.

### Recommendation
Bind `shop` (and ideally `topic`/`api_version`) into the HMAC-covered material for webhooks, mirroring what `Auth::Oauth::AuthQuery` already does for OAuth callbacks — e.g., have `Webhooks::Request#to_signable_string` include the shop domain and topic in a canonical signed string, or independently verify the delivered shop against a server-side record (e.g., confirm the shop is a currently-installed shop the app expects webhooks from) before dispatching to the handler. At minimum, update the documentation for `Registry.process`/`WebhookMetadata` to explicitly warn hosts that `shop` is unauthenticated and must not be trusted as a tenant boundary without additional verification.

### Proof of Concept
1. Install the target app on an attacker-controlled dev store (`attacker.myshopify.com`) and trigger any registered webhook topic (e.g., `orders/create`).
2. Capture the raw POST: body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's real `api_secret_key`, computed by Shopify).
3. Replay to the same app's public webhook endpoint with headers:
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: H` (unchanged)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - body `B` (unchanged)
4. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)`, which only checks `H` against `B` (see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`) — validation passes.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` even though the request never involved `victim-shop`, per `lib/shopify_api/webhooks/registry.rb:198-199`.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
