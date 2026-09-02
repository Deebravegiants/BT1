Confirmed: `Registry.process` passes `request.shop` (from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) straight into `WebhookMetadata`, which host apps use as the tenant identifier for the webhook payload, while the HMAC signature covers only `to_signable_string` (`@raw_body`) — the shop-domain header is never part of the signed bytes. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Title
Webhook shop-domain tenant identity is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator.validate` only covers the raw request body (`to_signable_string` returns `@raw_body`). `Registry.process` validates the HMAC and then forwards the unverified `shop` header value directly into `WebhookMetadata`, which is the tenant-identifying field host applications rely on to route/apply webhook data to the correct merchant.

### Finding Description
The identity binding that should hold is: `shop authenticated == shop the app acts on`. In this gem, the bytes verified by HMAC (`request.to_signable_string` → `@raw_body`) are not the bytes the shop identity is parsed from (`request.shop` → the `shop-domain` header). `Request#hmac` and `#to_signable_string` never touch the `shop-domain` header:

```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end

def to_signable_string
  @raw_body
end
``` [6](#0-5) 

`Registry.process` validates the HMAC of the body only, then trusts `request.shop` as the tenant key passed to the handler:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
``` [3](#0-2) 

An unprivileged internet user who has, or can guess/replay, one valid `(body, hmac)` pair for topic/body combination (or captures any legitimate webhook payload for a topic that host apps process generically, e.g. `orders/create`) can resend that exact body+hmac to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header for a *different* victim shop. Because the shop-domain header is excluded from the signed bytes, `HmacValidator.validate` still returns `true`, and `WebhookMetadata#shop` is populated with the attacker-chosen shop, even though it was never part of what Shopify actually signed for that payload.

### Impact Explanation
Host applications built on this gem are documented to trust `WebhookMetadata#shop` as the authenticated tenant for the webhook body. Because the shop is not bound to the HMAC, an attacker can present a validly-HMAC'd body under a spoofed shop domain, causing the host app to apply another merchant's webhook data (orders, customer data, redact requests, etc.) to a shop the attacker chooses — a cross-tenant data integrity/confidentiality breach. This matches the Critical "cross-tenant access" impact category since the identity boundary (`shop`) that gates which merchant's data is written/read is not authenticated.

### Likelihood Explanation
The attacker needs only network access to the app's public webhook endpoint and one legitimate `(raw_body, hmac)` pair for the topic in question (webhook payloads/HMACs are not shop-secret — the HMAC uses the app's single, non-shop-specific `client_secret`, so any two shops share the same signing key). No access token, `api_secret_key`, or privileged account is required, satisfying the unprivileged-internet-user constraint.

### Recommendation
Bind the shop identity into the signed material, or otherwise verify it independently before trusting it:
- Include the `shop-domain` header (and ideally `topic`, `webhook-id`) in the bytes hashed for `to_signable_string`, matching what's actually required to be trustworthy for downstream tenant routing, or
- Have `Registry.process` cross-check `request.shop` against the shop associated with the specific webhook subscription/session before invoking the handler, rather than trusting the header verbatim.

### Proof of Concept
1. Attacker captures/observes one valid webhook delivery to the app for shop `victim.myshopify.com` — obtains `raw_body` and its corresponding `x-shopify-hmac-sha256` value (both are visible to anyone who can register a webhook endpoint under any shop's app installation, or who has already-installed the app on their own shop and receives a body-shaped payload for a shared topic).
2. Attacker replays a POST to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com` (a shop they do not control).
3. `Utils::HmacValidator.validate` succeeds because it only checks `hmac(secret, raw_body)`, per `lib/shopify_api/utils/hmac_validator.rb:12-22` and `Request#to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38`.
4. `Registry.process` forwards `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` to the host app's handler at `lib/shopify_api/webhooks/registry.rb:188-200`, causing the host app to act on data attributed to `victim.myshopify.com` on the attacker's say-so.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
