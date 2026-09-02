## Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook forgery — (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the `shop` (tenant) is taken from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the HMAC-signed material. Any party holding one valid `(body, hmac)` pair signed with the app's secret (e.g. from their own store's webhook delivery) can replay it while substituting an arbitrary `shop-domain` header, and `Utils::HmacValidator.validate` will still report success, because the signature check never binds the header to the signature.

### Finding Description
`lib/shopify_api/webhooks/request.rb`:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`to_signable_string` is exactly `@raw_body`, so `shop` is a header value read directly and never mixed into the signable/verifiable material.

`lib/shopify_api/utils/hmac_validator.rb` validates the request purely against `verifiable_query.to_signable_string`:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [2](#0-1) 

`lib/shopify_api/webhooks/registry.rb#process` calls `Utils::HmacValidator.validate(request)` and, once it passes, forwards the *unauthenticated* `request.shop` straight to the app's handler as the tenant identity for the event:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

This is the exact "field acted on but not covered by the HMAC" identity-binding break. It is also visible by contrast within the same codebase: for the OAuth callback, `Auth::Oauth::AuthQuery#to_signable_string` explicitly folds `shop` into the signed parameter set so the shop cannot be swapped without invalidating the HMAC:
```ruby
def to_signable_string
  params = { code: code, host: host, shop: shop, state: state, timestamp: timestamp }
  URI.encode_www_form(params)
end
``` [4](#0-3) 

The webhook path deliberately (or by omission) fails to apply the same binding to the `shop` header, leaving:

`HMAC_verified(raw_body)` ⇏ `HMAC_verified(raw_body, shop)`

i.e. the equality the gem needs — "the shop the signature covers == the shop attributed to the event" — does not hold.

### Impact Explanation
Any unprivileged actor who can obtain one legitimately-signed `(body, hmac)` pair for the app (e.g., by installing the app themselves on a throwaway/free development store and capturing a real Shopify webhook delivery, since all shops using the app share the same `api_secret_key`) can replay that exact body+hmac to the app's public webhook endpoint while forging the `shop-domain` header to name any victim merchant. `HmacValidator.validate` still returns `true` because only `@raw_body` is checked, so `Registry.process` dispatches the handler with `shop:` set to the attacker-chosen victim domain and `body:` set to attacker-controlled JSON from their own store's event. Depending on how the host app's `WebhookHandler` uses `shop`/`body` (e.g. `MANDATORY_TOPICS` such as `shop/redact`, `customers/redact`, `customers/data_request`, or app-specific topics like `app/uninstalled`, `orders/create`), this enables cross-tenant data injection/corruption attributed to a shop the attacker does not control — a cross-tenant boundary break carrying the app's own trusted webhook channel.

### Likelihood Explanation
Moderate/low-but-concrete: it requires the attacker to obtain at least one legitimately HMAC-signed webhook body (trivially achievable by installing the app on a free dev store they control and triggering any subscribed topic), then send a crafted HTTP POST directly to the app's public webhook endpoint with a spoofed `shop-domain` header — no access token, no `api_secret_key`, and no privileged account is required.

### Recommendation
Bind the shop (and other externally-supplied identity fields such as `topic`, `api-version`, `webhook-id`) into the signable material, mirroring what `Auth::Oauth::AuthQuery#to_signable_string` already does for OAuth, e.g.:
```ruby
def to_signable_string
  "#{shop}\n#{topic}\n#{@raw_body}"
end
```
and recompute/verify against that combined string in `HmacValidator`, or otherwise cryptographically bind `shop-domain` (and `topic`) to the HMAC before trusting `request.shop` for dispatch in `Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and subscribes to a topic the target app handles (e.g., `customers/data_request`).
2. Shopify sends a legitimately signed webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, header `x-shopify-shop-domain = attacker.myshopify.com`.
3. Attacker captures `B` and its HMAC, then POSTs directly to the target app's public webhook endpoint with the same `raw_body = B` and same HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Webhooks::Request.new` parses this successfully (`lib/shopify_api/webhooks/request.rb`), and `Utils::HmacValidator.validate` returns `true` because it only recomputes HMAC over `@raw_body`, never over the shop header (`lib/shopify_api/utils/hmac_validator.rb` lines 26-31).
5. `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` and attacker-controlled `body: B`, despite the signature never having authenticated any relationship between `B` and `victim.myshopify.com` (`lib/shopify_api/webhooks/registry.rb` lines 188-200).

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
