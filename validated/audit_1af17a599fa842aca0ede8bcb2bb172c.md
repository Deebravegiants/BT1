## Analysis

The reachable bug class here is **"a field acted on but not covered by the HMAC."** In this gem, webhook authenticity is verified with `ShopifyAPI::Utils::HmacValidator.validate`, but the signed content is only the raw body — not the routing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) that the gem uses to dispatch the event to app logic. [1](#0-0) 

Specifically, `to_signable_string` (the value that gets HMAC-verified) returns only `@raw_body`: [2](#0-1) , while `topic`, `shop`, `api_version`, and `webhook_id` are read straight from unauthenticated HTTP headers: [3](#0-2) .

`Registry.process` validates only the body via `HmacValidator.validate(request)`, then immediately trusts the header-derived `topic`/`shop` to route the payload to the registered handler: [4](#0-3) .

### Equality that should hold but doesn't
`HMAC-verified(body)` is treated as if it implies `header.shop == originating_shop` and `header.topic == originating_topic`, i.e.:
`valid_hmac(raw_body) ⇒ (request.shop, request.topic) are authentic`

This equality does not actually hold, because `shop-domain`, `topic`, `webhook-id`, and `api-version` are never part of the signed bytes.

### Attack path
1. An unprivileged attacker installs the target app on their own store (no special privilege — this is the normal "unprivileged internet user" merchant flow) and triggers/captures one legitimate webhook delivery (`raw_body` + `x-shopify-hmac-sha256`) for a topic the app has registered, e.g. `orders/create`.
2. Since the HMAC covers only `raw_body`, this exact `(raw_body, hmac)` pair remains valid for **any** header values.
3. The attacker replays the same `raw_body`/`hmac` to the app's webhook endpoint, but sets `x-shopify-shop-domain` to a **different, victim** shop's domain (and/or a different `topic`/`webhook-id`).
4. `HmacValidator.validate` succeeds because it only checks the body against the real secret. `Registry.process` then calls the topic handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-chosen `shop`, not the shop that actually owns the signed payload.
5. Any host application that keys shop-scoped state (order sync, GDPR compliance actions, uninstall/reinstall bookkeeping, billing, etc.) off `WebhookMetadata#shop` will now perform that action against the victim shop's records, using data supplied by the attacker's own store — a cross-tenant identity binding break.

This is a root-cause issue in the gem itself (the `Request`/`Registry` design), not merely host-app misuse of a documented API: the gem's own `process` method is what forwards the unauthenticated header value as `shop`.

### Title
Webhook Shop/Topic Header Spoofing via HMAC Scope Gap - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only signs the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are taken verbatim from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC over the body only, then dispatches `WebhookMetadata` built from these unauthenticated headers to the app's webhook handler.

### Finding Description
`HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC. For webhooks, `to_signable_string` returns only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from the (attacker-controllable, unauthenticated) HTTP header map passed into `Request.new`. `Registry.process` validates only the body's HMAC and then trusts these header fields to build `WebhookMetadata` handed to the registered handler, without any cryptographic binding between the verified bytes and the shop/topic identity used for dispatch.

### Impact Explanation
An attacker who can obtain one valid `(raw_body, hmac)` pair for any topic (e.g., by triggering a real webhook on their own store) can replay it with a forged `shop-domain` header naming a different, victim tenant. Any consumer of `WebhookMetadata#shop` (the gem's own public interface for handler authors) will process the event as belonging to that victim shop, resulting in cross-tenant data corruption or logic execution attributed to the wrong merchant — meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Medium-High: the only prerequisite is the ability to receive one legitimate webhook delivery, which any merchant who installs the app can trigger themselves (e.g., by placing an order or editing a product), and then replay it against the app's public webhook endpoint with modified headers. No knowledge of `api_secret_key` or any other credential is required.

### Recommendation
Bind the shop/topic identity into the signed content path used for authorization decisions: after HMAC validation succeeds, do not trust `request.shop`/`request.topic` for cross-tenant-sensitive dispatch unless they are corroborated by an independent authenticated source (e.g., look up the webhook subscription by `webhook_id` via the Admin API using the session/shop the app already trusts, or maintain a server-side mapping from webhook registration to shop rather than trusting the header). At minimum, document loudly that `WebhookMetadata#shop`/`#topic` are NOT authenticated by the HMAC and must not be used as an authorization boundary without additional verification.

### Proof of Concept
```ruby
# Attacker's own store triggers a legitimate webhook, capturing:
raw_body = '{"id":123,"note":"legit order from attacker-owned shop"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)

# Attacker replays the exact same body+hmac but spoofs the shop-domain header
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,          # still valid: only body is signed
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
  "x-shopify-webhook-id" => "attacker-controlled-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes; handler.handle receives shop: "victim-shop.myshopify.com"
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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
