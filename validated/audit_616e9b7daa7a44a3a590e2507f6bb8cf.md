### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw HTTP body only, while the `shop`, `topic`, `api_version` and `webhook_id` values that are handed to the app's `WebhookHandler` are taken verbatim from unauthenticated HTTP headers. Since `Utils::HmacValidator.validate` only checks the body against the shared app secret, any party capable of producing one genuine, HMAC-valid webhook body/signature pair (e.g. from a shop they themselves control) can replay that exact body/signature with a forged `shop-domain` header to make the app process it as if it originated from a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` fields are read straight out of caller-supplied headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC over that signable string, then forwards the header-derived `shop` (and `topic`, `webhook_id`) straight to the app's handler without any additional cross-check that the shop is bound to the signature: [3](#0-2) 

`WebhookMetadata.shop` is a plain, unauthenticated `String` field consumed by the host application to key session/tenant lookups: [4](#0-3) 

The HMAC secret (`Context.api_secret_key`) is the app's single global client secret, shared across every shop that has installed the app — it is not scoped per-tenant: [5](#0-4) 

This reproduces the same root-cause pattern as the referenced report: a value that is *used* for a security-relevant decision (tenant/shop identity, analogous to `token0Amount`/`token1Amount` being consumed) is not actually constrained by the value that was *verified* (the HMAC, analogous to the dust calculation based on oracle price rather than the tick actually consumed). Concretely, the identity binding that should hold is:

`shop asserted to handler == shop bound by HMAC signature`

but the implementation only guarantees:

`body bytes verified by HMAC == body bytes parsed`

with `shop` sitting entirely outside that verified scope. Any app-installing shop (an "unprivileged" tenant relative to other tenants, requiring no admin access, no leaked token, and no knowledge of `api_secret_key`) can:
1. Trigger a webhook delivery to their own shop for a topic they control (e.g. `orders/create`), capturing the genuine `raw_body` and its valid `x-shopify-hmac-sha256`.
2. Replay that exact `raw_body`/HMAC pair to the app's public webhook endpoint while substituting `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) with a victim shop's domain.
3. `HmacValidator.validate` still succeeds because it only checks `raw_body` against the shared secret; `Registry.process` then invokes the handler with `shop: "<victim-shop>.myshopify.com"`.

Because host applications are documented to trust `WebhookMetadata.shop` as the authenticated tenant identity for looking up sessions/credentials and applying webhook data, this breaks the cross-tenant boundary that the HMAC is supposed to enforce.

### Impact Explanation
This qualifies as Critical — cross-tenant access. An attacker with only a normal, low-privilege install of the app (their own shop, no special access, no leaked secrets) can make the app believe a crafted payload/topic originated from an arbitrary other merchant's shop. Depending on how the host app trusts `data.shop` (session lookup, order/customer data ingestion, triggering shop-scoped side effects), this can lead to data corruption, unauthorized actions attributed to a victim shop, or triggering privileged-looking flows (e.g. `app/uninstalled`, `shop/redact`) against a shop the attacker does not own.

### Likelihood Explanation
Likelihood is high for any app that has at least one active install (the attacker only needs to be a legitimate, if unprivileged, merchant using the app) and exposes its webhook endpoint publicly, which is required by design. No secret material, TLS interception, or social engineering is needed — only the ability to receive one genuine webhook and replay it with modified headers.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed payload (or otherwise cryptographically bind them to the body before verification), and/or require the host application to cross-check the header-derived `shop` against a shop the app actually expects/has a session for before trusting `WebhookMetadata.shop`. At minimum, document prominently that `Request#shop`/`topic`/`webhook_id` headers are unauthenticated and must not be trusted as tenant identity without additional verification.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the app,
# so Shopify delivers a genuine, validly-signed webhook to the app's endpoint:
#
#   x-shopify-topic: orders/create
#   x-shopify-hmac-sha256: <valid HMAC over raw_body>
#   x-shopify-shop-domain: attacker-shop.myshopify.com
#   raw_body: '{"id":1,...}'
#
# The attacker captures raw_body + hmac (both are visible to them since it's
# their own installation's webhook), then replays the identical body/HMAC to
# the same endpoint with a forged shop header:

headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_valid_hmac,   # unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: headers)

# Utils::HmacValidator.validate(request) still returns true, because
# to_signable_string only returns raw_body, which was never altered.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```
`Registry.process` never rejects this request; the handler receives `shop: "victim-shop.myshopify.com"` despite the payload never having been produced or signed for that shop. [6](#0-5) [7](#0-6)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
