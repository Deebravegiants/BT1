Confirmed: the HMAC binds only the raw request body via `to_signable_string` returning `@raw_body`, while `topic`, `shop`, `api_version`, and `webhook_id` are all read straight from unauthenticated HTTP headers.### Title
Webhook HMAC covers only the raw body, not the `shop-domain`/`topic`/`webhook_id` headers, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` from unauthenticated HTTP headers, while the HMAC signature verified by `HmacValidator` only covers the raw request body (`to_signable_string` returns `@raw_body`). `Registry.process` trusts `request.shop` and passes it straight into `WebhookMetadata`, which host applications use to attribute the webhook to a tenant/session. This breaks the identity binding: `hmac(body) == valid` is treated as proof that `shop-domain header == true origin shop`, but the header is never part of the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are read verbatim from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` compute the HMAC only over `verifiable_query.to_signable_string` (the body) using the app's single, shop-independent `Context.api_secret_key`: [3](#0-2) 

`Registry.process` validates only this body HMAC, then forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` unchecked into `WebhookMetadata`, which the host app's handler consumes as the trusted tenant identity for the event: [4](#0-3) [5](#0-4) 

Because the same `api_secret_key`/`client_secret` is shared across every shop that installs the app, an unprivileged internet user who installs the app on their own (attacker-controlled) development shop can legitimately receive a webhook with a valid `(raw_body, hmac)` pair. Since `shop-domain`, `topic`, and `webhook_id` are not covered by that HMAC, the attacker can replay the exact same body+hmac to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`, `x-shopify-webhook-id`) with a victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks the (unchanged) body against the (unchanged) signature — the equality it actually enforces is `hmac(body, secret) == received_hmac`, not `hmac(body ∥ shop ∥ topic, secret) == received_hmac`. The handler then processes attacker-supplied/attacker-timed event data as if it originated from the victim's shop, corrupting or exfiltrating data keyed by `shop` in the host application (e.g., mandatory `customers/redact`/`shop/redact`/`customers/data_request` handlers, or any app-specific per-shop side effect keyed by `WebhookMetadata#shop`).

### Impact Explanation
This is a cross-tenant authentication/identity-binding bypass: the gem gives host applications no way to know that the `shop` field they act on was ever covered by the cryptographic proof they just validated. An attacker with no access to any victim credentials can make the app believe an event belongs to a different, arbitrary shop, meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Exploitation only requires: (1) being able to install the app on any shop — including a free/trial dev store, which is available to any unprivileged internet user, and (2) capturing one real webhook delivery to obtain a valid `(body, hmac)` pair, then replaying it with a modified `shop-domain` header to the app's public webhook endpoint. No secrets, tokens, or privileged access are needed. The library performs no defense against this by design of `to_signable_string`/`process`, so likelihood is high wherever a host app trusts `WebhookMetadata#shop`/`#topic`/`#webhook_id` for tenant-sensitive logic (which is the documented purpose of these fields).

### Recommendation
Bind the tenant-identifying headers into the verified signature material, or independently verify them against the session/shop the app expects, before constructing `WebhookMetadata`. Concretely: include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (or otherwise cryptographically bind them), or require the caller to supply/validate the expected shop out-of-band and compare it to `request.shop` prior to invoking the handler in `Registry.process`.

### Proof of Concept
1. Attacker registers the target app on their own shop `attacker.myshopify.com` and enables an HTTP webhook (e.g., `orders/create`).
2. Attacker triggers the event, capturing the real delivery: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)` — valid because `HmacValidator.validate_signature` only checks `H` against `B`. [6](#0-5) 
3. Attacker replays an HTTP POST to the app's webhook endpoint with unchanged body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and/or an arbitrary `x-shopify-webhook-id`/topic already registered by the app).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B`/`H`. [7](#0-6) 
5. The handler executes with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, and the app performs shop-scoped side effects attributed to `victim.myshopify.com` even though the event never originated from that shop. [8](#0-7)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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
