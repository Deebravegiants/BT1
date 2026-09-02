This confirms the vulnerability clearly. `AuthQuery#to_signable_string` correctly binds `shop`, `code`, `host`, `state`, and `timestamp` into the signed payload [1](#0-0) , but `Webhooks::Request#to_signable_string` returns only `@raw_body`, leaving `shop`, `topic`, `webhook_id`, and `api_version` headers completely outside the HMAC-signed content [2](#0-1) . `Registry.process` validates only that the body's HMAC is correct, then trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` taken straight from unauthenticated headers to build `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Title
Webhook shop/topic identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers are read unauthenticated and forwarded as trusted identity fields to the host application's webhook handler.

### Finding Description
`Registry.process` calls `Utils::HmacValidator.validate(request)` [4](#0-3) , which computes the HMAC over `verifiable_query.to_signable_string` [5](#0-4) . For webhooks, `to_signable_string` returns only `@raw_body` [2](#0-1) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors are read directly from HTTP headers with no cryptographic binding to that signature [6](#0-5) .

Immediately after validation succeeds, `Registry.process` uses `request.topic` to look up the handler and constructs `WebhookMetadata` from `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all header-derived, unsigned values — and passes this to the host application's handler as if it were authenticated data [7](#0-6) .

This breaks the intended identity binding: `HMAC-valid == request came from the shop named in the headers`. In reality the equality that holds is only `HMAC-valid == raw_body was signed with api_secret_key`; nothing ties the signature to the `shop`/`topic`/`webhook_id` header values used downstream.

### Impact Explanation
An unprivileged attacker who has installed the app on their own store (no special privileges — this is a normal, self-service Shopify app install) will receive genuine webhooks from Shopify with valid HMAC signatures computed over the body. Because the signature covers only the body, the attacker can replay that exact HTTP request to the app's public webhook endpoint while rewriting `x-shopify-shop-domain` to any victim shop's domain (and/or `x-shopify-topic`/`x-shopify-webhook-id`/`x-shopify-api-version`) without invalidating the HMAC check performed by this gem. The host application, trusting `request.shop`/`WebhookMetadata#shop` as the authenticated tenant identity (a standard and expected usage pattern for this library), will process attacker-controlled body data under the victim shop's identity — a cross-tenant confusion where data attributed to one merchant is injected under another merchant's identity in the host app's data model.

### Likelihood Explanation
Any user can self-install the app to obtain a legitimately signed webhook, then trivially resend it over HTTP with modified headers to the public webhook endpoint. No secret material, privileged account, or network interception is required — only the ability to send an HTTP request and knowledge of a target shop domain.

### Recommendation
Include the `shop`, `topic`, `api_version`, and `webhook_id` header values in `Webhooks::Request#to_signable_string` (or otherwise cryptographically bind them, e.g., via a canonical string of `raw_body + headers`), so any header tampering invalidates the HMAC check performed in `Utils::HmacValidator.validate`. At minimum, the `shop` field used for tenant attribution must be covered by the signature before being exposed via `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the raw POST: body `B`, and headers including `x-shopify-hmac-sha256: H` (valid for `B` per `Request#to_signable_string`/`HmacValidator.validate`), `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker resends the identical body `B` and HMAC header `H` to the app's public webhook endpoint, but replaces `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only [5](#0-4)  and it matches `H`, so validation passes.
4. `Registry.process` builds `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: parsed(B), ...)` [8](#0-7)  and dispatches it to the app's handler, which processes attacker-supplied order data as though it belongs to `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L27-31)
```ruby
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
