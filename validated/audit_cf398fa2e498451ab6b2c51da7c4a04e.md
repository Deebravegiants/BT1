This confirms the vulnerability. I have sufficient evidence to finalize the analog.

### Title
Webhook `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used downstream to attribute and dispatch the webhook are read from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only that the body's HMAC is genuine, then blindly trusts the header-derived `shop` field when building `WebhookMetadata` passed to the host app's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all derived from HTTP headers that are not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, and then unconditionally trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build the `WebhookMetadata` object handed to the app's registered handler: [3](#0-2) 

`WebhookMetadata` is a plain struct with no independent verification of `shop`: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`bytes_covered_by_hmac(request) == identity_fields_used_by_handler(request)`

Before the attacker's request: for a genuine Shopify-originated webhook, `raw_body` is HMAC-signed by Shopify using `api_secret_key`, and the accompanying `shop-domain` header correctly names the shop that produced that body.

After the attacker's request: any party who can obtain one validly-signed `(raw_body, hmac)` pair for *any* shop that installed the app (e.g., their own store, on which they are a legitimate merchant/admin) can resend that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`/`shopify-api-version`) header value. `Utils::HmacValidator.validate` will still return `true` because it only recomputes the HMAC over `raw_body`, so `Registry.process` proceeds and calls the app's handler with `WebhookMetadata#shop` set to the attacker-chosen shop domain rather than the shop that actually generated the body.

This is a direct, reachable path in the gem's own code (not `lib/shopify_api/rest/resources/**`, not test code) and does not require the app's `api_secret_key`, an access token, or any privileged account — only the ability to legitimately trigger a webhook-producing event on any shop that has installed the app (something any merchant/store owner can do for their own store).

### Impact Explanation
This crosses a tenant boundary: an unprivileged actor operating one tenant (shop) can cause the host application to process webhook data under the identity of a different tenant. Any host application that uses `WebhookMetadata#shop` to select which merchant's session/data record to update (the exact documented usage pattern in `docs/usage/webhooks.md`) can be tricked into writing/reading data attributed to a shop the attacker doesn't control, or into triggering shop-scoped side effects (e.g., app uninstall handling, data-sync, order-processing side effects) for a victim tenant. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high: the attacker only needs a legitimate account with any shop that has the target app installed (trivial to obtain for many apps, e.g. free/dev-store installs) to generate at least one real, HMAC-signed webhook body/signature pair, then replay it with a forged `shop-domain` header value at will. No secret material or privileged access is required, and the replay can be repeated for any topic the attacker can trigger on their own store.

### Recommendation
Include the shop domain (and ideally the topic, webhook id, and api version) inside the HMAC-covered signable string, or independently authenticate the `shop` value against the body/session context before constructing `WebhookMetadata`. At minimum, `Request#to_signable_string` should bind `shop` cryptographically so that a body signed for shop A cannot be replayed and attributed to shop B.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com` (any account can do this).
2. Attacker triggers a webhook-producing event on their own shop (e.g., `orders/create`), causing Shopify to POST a `raw_body` with a valid `x-shopify-hmac-sha256` header and `x-shopify-shop-domain: attacker-shop.myshopify.com` to the app's webhook endpoint.
3. Attacker captures this exact `(raw_body, hmac_header)` pair.
4. Attacker resends the same `raw_body` and `hmac_header` to the app's webhook endpoint, but replaces the header `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and optionally alters `x-shopify-topic`/`x-shopify-webhook-id`).
5. `Utils::HmacValidator.validate` in [5](#0-4)  
returns `true` because it only checks `raw_body`'s signature.
6. `Registry.process` proceeds and invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the host app to process (attacker-controlled) order/product/etc. data as if it belonged to the victim shop.

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
