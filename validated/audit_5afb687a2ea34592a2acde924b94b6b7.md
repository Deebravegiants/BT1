## Title
Webhook shop/topic/webhook-id identity is not covered by the HMAC signature, allowing cross-tenant webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable payload from the raw request body only. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — which the gem hands to the app's webhook handler as the trusted tenant/event identity — are never included in the signed material. Anyone who can obtain one legitimate `(body, hmac)` pair for their own shop (e.g. by installing the app on their own store, which any unprivileged internet user can do) can replay that exact body/hmac pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (and topic/webhook-id) header. `Utils::HmacValidator.validate` will report the request as authentic, and `Webhooks::Registry.process` will hand the handler a `WebhookMetadata` claiming the attacker-chosen shop, even though only the body was ever proven authentic — breaking the equality `hmac-verified request == claimed shop`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read directly from unauthenticated headers, with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC purely over `verifiable_query.to_signable_string`, i.e. the raw body: [3](#0-2) 

`Webhooks::Registry.process` trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which were part of the HMAC check — once `HmacValidator.validate` passes, and forwards them unchecked to the application handler: [4](#0-3) 

This differs from `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` (and `host`, `code`, `state`, `timestamp`) are all included in `to_signable_string` and therefore *are* bound by the HMAC: [5](#0-4) 

The webhook path has no equivalent binding: the identity fields consumed by the handler (`shop`, `topic`, `webhook_id`) are disjoint from the fields covered by the signature (`raw_body` only).

### Impact Explanation
An attacker who has installed the app on any shop they control (an ordinary, unprivileged action) will legitimately receive webhooks with valid `(body, hmac)` pairs for events on their own store. Because the HMAC never covers the shop-domain/topic/webhook-id headers, the attacker can resend that same body+hmac to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a victim shop (and/or a forged topic such as `app/uninstalled`, `shop/redact`, `customers/data_request`, etc.). `HmacValidator.validate` still returns true because the body signature matches, and `Registry.process` builds `WebhookMetadata` using the attacker-controlled `shop`/`topic` values, which the host application's handler will treat as authentic per this gem's documented contract. Depending on the handler's business logic this enables cross-tenant state changes (e.g. incorrectly marking a victim shop's app as uninstalled, triggering GDPR data-erasure actions against the wrong tenant, or otherwise mutating another merchant's stored data) — a cross-tenant access/integrity impact.

### Likelihood Explanation
Likelihood is moderate-to-high: no access token, `client_secret`, or privileged account is required — only the ability to install the target app on any shop (including the attacker's own free/dev store), which is the normal, expected path for any Shopify app. The header spoofing itself requires only direct HTTP access to the app's public webhook endpoint.

### Recommendation
Bind the identity fields into the signed payload verification path: either (a) include `shop-domain`, `topic`, and `webhook-id` in the string that gets HMAC-verified (mirroring what `AuthQuery#to_signable_string` already does for OAuth), or (b) have the application layer additionally verify that `request.shop` matches an expected/registered shop for the resolved webhook subscription before trusting it, and document this requirement prominently since the gem currently implies these fields are safe to consume once `HmacValidator.validate` succeeds.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, receiving a legitimate webhook delivery, e.g. for `customers/data_request`:
   - Headers: `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: customers/data_request`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`
   - Body: `{"shop_id":111,...}`
2. Attacker replays the exact same body and HMAC header to the app's public webhook endpoint, but changes only:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
3. The app constructs `ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)` and calls `ShopifyAPI::Webhooks::Registry.process(request)`.
4. `Utils::HmacValidator.validate` succeeds because it only rehashes `raw_body`, which is unchanged.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: "customers/data_request", shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the app to perform tenant-scoped logic against `victim-shop.myshopify.com` on the attacker's behalf.

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
