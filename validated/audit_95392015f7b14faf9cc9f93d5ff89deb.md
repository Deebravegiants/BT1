### Title
Webhook `shop`, `topic`, `api-version`, and `webhook-id` fields are trusted from unauthenticated headers while only the raw body is HMAC-verified - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, but its `to_signable_string` returns only `@raw_body` [1](#0-0) . `Registry.process` accepts the request as authentic once `Utils::HmacValidator.validate(request)` succeeds against that raw body [2](#0-1) , then builds `WebhookMetadata` using `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` — all of which are parsed straight from HTTP headers (`shop`, `topic`, `webhook-id`, `api-version`) and are never part of the signable string [3](#0-2) [4](#0-3) .

### Finding Description
The identity binding that should hold is: `hmac_secret_key == the app's single shared api_secret_key used for every shop that installs the app`, and the code implicitly relies on `hmac_valid(body) → data.shop is trustworthy`. That equality is false — `HmacValidator.validate` only proves the **body bytes** were signed with the app's `api_secret_key` [5](#0-4) ; it says nothing about which shop, topic, webhook id, or API version the body belongs to, because those fields are excluded from `to_signable_string`.

Because `api_secret_key` is one value per app, shared across every merchant who installs that app, any tenant of the app receives genuine webhook deliveries HMAC'd with that same shared secret. An attacker who controls one (even the least-privileged) shop that installs the target app can capture a real, validly-signed `(raw_body, hmac)` pair delivered to their own endpoint, then replay that exact body/HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, and `X-Shopify-Api-Version` headers to claim they belong to a victim shop. `HmacValidator.validate` still passes because it only checks the raw body against the shared secret, so `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain [6](#0-5)  and `WebhookMetadata#topic` set to whatever the attacker claims, even though neither value was cryptographically bound to that body.

This is the exact analog of the reported bug class: a field that is *acted on* by downstream logic (`shop`, used by host applications to route data/side effects to a specific merchant's tenant) is not covered by the authentication mechanism (`HMAC`) that is supposed to establish trust in the request.

### Impact Explanation
Any handler that uses `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) to decide which merchant's records to update, without independently re-validating that the shop actually owns that webhook subscription, can be fed attacker-controlled, cross-tenant webhook events. Because the shared api_secret_key makes the HMAC forgeable-by-content-reuse across tenants, this crosses a tenant boundary using only unprivileged access to any shop that installs the app — no access token, no `client_secret`, and no TLS interception is required, satisfying the "cross-tenant access" high/critical impact category.

### Likelihood Explanation
Exploitation requires: (1) installing the target app on an attacker-controlled shop (or otherwise obtaining any one legitimate webhook delivery for that app), (2) sending an HTTP POST to the app's webhook endpoint with the captured body/HMAC but forged `X-Shopify-Shop-Domain`/`X-Shopify-Topic` headers. Both steps are achievable by an unprivileged internet user with no special credentials, making likelihood moderate-to-high, contingent on the host application trusting `WebhookMetadata#shop`/`#topic` for authorization decisions (which is the documented intended use of these fields per `docs/usage/webhooks.md` and the `WebhookHandler` interface) [7](#0-6) .

### Recommendation
**Short term:** Extend `VerifiableQuery#to_signable_string` for `Webhooks::Request` (or add a separate check in `Registry.process`) to bind `shop`, `topic`, `webhook_id`, and `api_version` into the value that is HMAC-verified, or otherwise cross-check `request.shop` against the session/shop that the app expects for that webhook subscription before dispatching to the handler.

**Long term:** Avoid trusting any header-derived identity field (`shop`, `topic`) that is not cryptographically bound to the same integrity check used to authenticate the payload; treat unauthenticated header values as attacker-controlled by default.

### Proof of Concept
```ruby
# Attacker owns/installs the app on shop "attacker.myshopify.com" and
# receives a real webhook, e.g. orders/create, with a genuine HMAC
# computed by Shopify using the app's shared api_secret_key:
#
#   headers:
#     x-shopify-topic: orders/create
#     x-shopify-hmac-sha256: <valid HMAC of body using api_secret_key>
#     x-shopify-shop-domain: attacker.myshopify.com
#   body: '{"id":1,"note":"hello"}'
#
# Attacker replays the identical body + hmac, but swaps only the
# shop-domain header to a victim shop:
headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => captured_valid_hmac,   # unchanged
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
}
request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: headers)

# Passes because HMAC only covers @raw_body, not the shop header:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```
`Utils::HmacValidator.validate` re-derives the signature solely from `to_signable_string` (the raw body) [1](#0-0) [8](#0-7) , so the forged `shop` header passes straight through to the handler unauthenticated [4](#0-3) .

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
