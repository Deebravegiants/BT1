### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` values used to route and attribute the webhook are taken from unauthenticated HTTP headers. This breaks the identity binding `HMAC-signed-bytes == bytes-acted-on`, letting a party who can produce a validly-HMAC'd body (e.g., the operator of one shop that has installed the app, since a single app's webhook signing secret — `api_secret_key` / `client_secret` — is shared across every shop that installs the app) replay that body while forging the `shop` header to impersonate a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `hmac` accessor also derives its comparison value only from the `hmac-sha256` header, but the `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from separate, unsigned headers: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (i.e., the body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` uses this HMAC check as its sole authentication gate, then trusts `request.shop` (and the other header-derived fields) to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) [5](#0-4) 

Because the HMAC only binds the body, not the headers, the equality the code actually needs — `hmac_signed(shop, topic, body) == verified(shop, topic, body)` — is instead only `hmac_signed(body) == verified(body)`. Any request whose body+HMAC pair is valid (signed with the app's shared `api_secret_key`) will pass verification regardless of what `shop`/`topic`/`webhook_id` headers accompany it.

In real Shopify webhook delivery, the signing secret used for HMAC is the app's `client_secret`/`api_secret_key`, which is identical for every shop that has installed the same app — it is not shop-specific. Consequently, a user who legitimately operates their own shop under the app receives real, validly-signed webhook deliveries for their own shop's data. Nothing in this gem prevents them from replaying that body (with its still-valid HMAC) to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at another tenant. `Registry.process` will validate the HMAC successfully and dispatch the handler with `WebhookMetadata#shop` set to the forged/victim shop, causing the app to process attacker-controlled data attributed to a shop the attacker does not control — a cross-tenant data-integrity/confusion issue.

### Impact Explanation
This falls under the Critical category of "cross-tenant access": an unprivileged user who legitimately controls one tenant (their own installed shop) can cause the host application to process forged webhook data under another tenant's identity, without needing the app's secret, an access token, or any privileged access — they only need a webhook delivery from their own shop, which Shopify sends them by design.

### Likelihood Explanation
Likelihood is high for any consumer of this gem that trusts `WebhookMetadata#shop` (or `#topic`) for authorization or tenant-scoping decisions without independently cross-checking it — this is the documented, intended usage pattern shown in the gem's own webhook processing example (`Registry.process` is the only verification step performed). Because signing secrets are shared per-app across all installed shops, any merchant who has installed the app (a normal, unprivileged action) can obtain valid body/HMAC pairs to replay.

### Recommendation
Bind the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) into the HMAC signable string, or otherwise cryptographically verify them (Shopify does not sign headers by design, so at minimum the gem should require the caller to supply an expected shop and abort processing if `request.shop` does not match), and document clearly that `Registry.process`'s HMAC validation only authenticates the body and does not authenticate the shop/topic headers, so integrators must independently validate `request.shop` against the session/tenant they expect before trusting `WebhookMetadata`.

### Proof of Concept
1. App `X` is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both signed with the same `api_secret_key` for app `X`.
2. Shopify delivers a legitimate webhook to the attacker for `attacker-shop.myshopify.com` with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker replays this exact body `B` and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header set; `Utils::HmacValidator.validate` succeeds because it only checks `B` against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to act on attacker-supplied data as if it belonged to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
