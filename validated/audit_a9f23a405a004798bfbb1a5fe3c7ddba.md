### Title
Webhook `shop` and `topic` headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the `shop`, `topic`, `api_version`, and `webhook_id` fields — read directly from unauthenticated HTTP headers — are trusted and forwarded to the app's webhook handler. This breaks the binding between "bytes verified by HMAC" and "shop/topic acted upon by the handler."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only the HMAC over the raw body, then immediately trusts `request.shop` (and `request.topic`) to dispatch the webhook to the app's handler as the tenant identity for the event: [3](#0-2) 

Contrast this with `Auth::Oauth::AuthQuery`, where the shop field IS included in the signed content: [4](#0-3) 

This is exactly the identity-binding gap named in scope: "a field acted on but not covered by the HMAC." Since `shop-domain` is not part of `to_signable_string`, `OpenSSL.secure_compare(computed_signature, received_signature)` in `HmacValidator.validate_signature` verifies only that the *body bytes* were signed with the app's secret — not that they were signed *for this shop*: [5](#0-4) 

Concretely: a merchant who has installed the app (and thus can trigger/observe genuine webhooks carrying a valid `x-shopify-hmac-sha256` for a given raw body under the app's single shared `api_secret_key`) can replay that exact raw body with a forged `x-shopify-shop-domain` header naming a different shop that also has the app installed. `HmacValidator.validate` still returns `true` because it only checks the body signature, and `Registry.process` passes the attacker-chosen `shop` value into `WebhookMetadata`, which the app's handler will treat as authentic. Any host app that uses `request.shop` from the webhook metadata to select which tenant's data to update (the intended and documented use of this field) will apply the payload to the wrong tenant — a cross-tenant write/read primitive using only the gem's own webhook-processing code path.

### Impact Explanation
This enables cross-tenant confusion: an attacker who is a legitimate (if malicious) merchant of the app can cause data intended for their own shop to be attributed to another shop using the same app installation, or vice versa, without ever needing the `client_secret` beyond what's needed to receive their own valid webhooks. This matches the Critical "cross-tenant access" impact bucket defined in scope, since the binding between the authenticated bytes (body) and the acted-upon tenant identity (`shop`) is not enforced by the gem.

### Likelihood Explanation
Likelihood is meaningful but not trivial: it requires the attacker to control (or observe) a shop that has the target app installed so they can obtain a body/HMAC pair signed with the app's shared secret, then replay it with a forged `shop-domain` header to the app's webhook endpoint. No `api_secret_key` or access-token theft is required — only normal use of a merchant account plus header manipulation on the replayed HTTP request, both of which are unprivileged-internet-user-reachable.

### Recommendation
Include `shop`, `topic`, and any other headers the handler relies on for identity/authorization decisions in the HMAC-signable content (as `AuthQuery` already does for OAuth), or otherwise cryptographically bind these header values to the payload signature, so `HmacValidator.validate` cannot succeed for a body that has been paired with a shop/topic other than the one it was originally signed for.

### Proof of Concept
1. App has two shops installed: `shop-a.myshopify.com` (attacker-controlled) and `shop-b.myshopify.com` (victim).
2. Attacker triggers an event on `shop-a` causing Shopify to send a webhook with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker resends the same body `B` and same HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only checks `B` against the same secret — see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: parsed(B), ...)`, causing the app to process shop-a's data as if it belonged to shop-b — see `lib/shopify_api/webhooks/registry.rb:198-199`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
