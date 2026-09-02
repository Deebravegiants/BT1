### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant-identity spoofing on replayed webhooks - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only. The `shop` (and `topic`, `api_version`, `webhook_id`) values are taken from unauthenticated HTTP headers and are never included in the signed payload. `Registry.process` trusts `request.shop` and hands it directly to the app's `WebhookHandler` as the tenant identity, so any actor who can present a valid `(body, hmac)` pair can attach an arbitrary `shop-domain` header to it and have the app process the webhook as if it came from a different shop.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

while `shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header without any binding to the signature: [2](#0-1) 

`HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` accepts the request once this body-only HMAC check passes, and forwards `request.shop` — the unsigned header — as the trusted tenant identifier to the app's handler: [4](#0-3) [5](#0-4) 

This is the exact identity-binding gap the reference report describes for DYAD: **bytes verified (the HMAC covers only the body) versus bytes/fields acted on (the `shop` field used to identify the tenant)**. Because the `shop-domain` header sits entirely outside the HMAC-signed content, its value can be swapped after the signature was computed without invalidating the signature.

The documented processing pattern confirms the header is fully attacker-reachable at the HTTP layer, since the gem simply wraps `request.headers.to_h` from the raw web request with no additional origin check: [6](#0-5) 

### Impact Explanation
An unprivileged actor who can install the app on their own (attacker-controlled) shop will legitimately receive real webhook deliveries from Shopify — a valid `(raw_body, hmac)` pair signed with the app's `api_secret_key`, but carrying only their own shop's data. Since the `shop-domain` header is not part of the signed content, the attacker can replay that same body+HMAC to the app's webhook endpoint while substituting a victim shop's domain in the `shopify-shop-domain` header. The HMAC check still passes (only the body matters), and `WebhookMetadata#shop` will report the attacker-chosen domain to the handler. If the app uses `data.shop` to select which merchant's session/data to act on (the pattern explicitly shown in the gem's own docs, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), the attacker can inject fabricated events attributed to an arbitrary victim shop — a cross-tenant identity confusion enabled entirely within this gem's webhook verification code, satisfying the "cross-tenant access" Critical-impact criterion without needing any credentials, access tokens, or `client_secret` of the victim.

### Likelihood Explanation
Likelihood is high for any attacker who can install the target app (a normal, unprivileged action for any Shopify merchant/developer) since that alone yields a validly-signed webhook body+HMAC pair. No secret material belonging to the victim or the app is required — only a replay of a previously captured legitimate delivery with a modified, unsigned header. The only prerequisite is that the app's handler trusts `data.shop` for tenant scoping, which is exactly the pattern the gem's own documentation recommends.

### Recommendation
Bind the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) header value into the HMAC-signed content, or otherwise cryptographically tie the header claims to the payload before exposing them to the handler. At minimum, `Request#to_signable_string` should incorporate the shop domain the app is about to trust, so that altering the header invalidates the signature — mirroring how `Utils::VerifiableQuery` binds all OAuth callback fields (`code`, `host`, `shop`, `state`, `timestamp`) into `AuthQuery#to_signable_string` before HMAC validation.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers for a webhook topic (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(B, api_secret_key)`, header `x-shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker replays the request to the app's webhook endpoint, keeping `raw_body = B` and the same `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: replayed_headers)` computes `hmac` from the (unchanged) header and `to_signable_string` returns `B` unchanged, so `HmacValidator.validate` in [7](#0-6)  returns `true`.
5. `Registry.process` at [8](#0-7)  calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop.

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

**File:** docs/usage/webhooks.md (L125-136)
```markdown
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
