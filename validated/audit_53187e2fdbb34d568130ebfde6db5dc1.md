This confirms the vulnerability: `Registry.process` validates only the HMAC over the raw body via `Utils::HmacValidator.validate(request)`, whose `to_signable_string` returns `@raw_body` alone [1](#0-0) . The `shop-domain` header used for tenant attribution (`request.shop`) is read directly from an HTTP header and is never included in the HMAC-signed material [2](#0-1) . `Registry.process` passes this unauthenticated `shop` value straight into the handler as the tenant identifier [3](#0-2) .

### Title
Webhook `shop-domain` Header Is Not Covered by HMAC, Allowing Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC signature only to the raw request body, while the `shop` (tenant identifier) is read from the `X-Shopify-Shop-Domain` HTTP header, which is not part of the signed data. `Registry.process` verifies the HMAC and then trusts `request.shop` to determine which merchant/tenant the webhook belongs to, without any binding between the signature and that header.

### Finding Description
The library's own `VerifiableQuery` contract requires each verifiable request to expose the exact bytes that were signed via `to_signable_string`, and `HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it against the `hmac` value [4](#0-3) . For webhooks, `to_signable_string` returns only `@raw_body` [1](#0-0) , so the signature proves only that the *body bytes* were produced by Shopify with the app's secret — it says nothing about which shop sent it. The `shop`, `topic`, `api_version`, and `webhook_id` values are all parsed from HTTP headers outside the signed scope [5](#0-4) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`) as the identity of the tenant that generated the webhook, forwarding it to the app's handler as `WebhookMetadata` [6](#0-5) .

This breaks the intended binding: `shop authenticated by the HMAC == shop the handler is told the webhook came from`. In reality the equality that holds is only `body authenticated by HMAC == raw body bytes`; the `shop-domain` header is fully attacker-controllable metadata layered on top of a signature that never covers it.

An attacker who is an unprivileged internet user, but who legitimately controls at least one shop with the app installed (a normal, unprivileged installation — not a privileged/oDAO-style account, and requiring no access to `api_secret_key` or any merchant's access token), can:
1. Install the app on their own store (Shop A) and trigger a webhook (e.g. `orders/create`) with attacker-chosen order data, causing Shopify to send a validly-HMAC-signed webhook request to the app's public webhook endpoint.
2. Capture that valid `(raw_body, hmac)` pair.
3. Replay the same body/HMAC to the app's webhook endpoint, but override the `X-Shopify-Shop-Domain` header to name a victim shop (Shop B).
4. `Utils::HmacValidator.validate` still succeeds, because the HMAC only ever covered the body, and `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and the attacker's chosen body content.

Any host application that uses `request.shop`/`WebhookMetadata#shop` to select which tenant's records to update (a normal and expected usage pattern for a multi-tenant webhook handler) will act on attacker-controlled webhook data as if it originated from the victim's shop, resulting in cross-tenant data corruption/injection.

### Impact Explanation
This is a cross-tenant integrity/isolation violation: an attacker who is a legitimate, unprivileged user of the app on their own store can forge a webhook that the app attributes to a different merchant's tenant, entirely bypassing the identity guarantee that the HMAC is supposed to provide. This matches the "Critical - cross-tenant access" impact category, since the shop-domain binding is the sole tenant boundary the app has for webhook-driven state changes.

### Likelihood Explanation
Likelihood is high for any app that trusts `request.shop`/`WebhookMetadata#shop` for tenant routing (the documented, expected usage) and exposes a single shared public webhook endpoint (the standard Shopify app pattern). Exploitation requires only: (a) attacker owns/controls a store with the app installed, (b) attacker can trigger any webhook topic with content they control, and (c) attacker can send an arbitrary HTTP request with custom headers to the app's public webhook endpoint — no secrets, tokens, or privileged access are required.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`, `api-version`, `webhook-id`) in the HMAC-signed material, or require the host application to independently verify that `request.shop` corresponds to a shop that legitimately owns the webhook subscription (e.g., cross-reference against a stored shop→webhook-id mapping) before trusting it. At minimum, `Utils::HmacValidator` should be validating a canonical string that binds shop identity to body, e.g., changing `Webhooks::Request#to_signable_string` to include `shop` (and `topic`) alongside `@raw_body`, mirroring how `Oauth::AuthQuery#to_signable_string` binds `shop`, `state`, `code`, etc. together in `lib/shopify_api/auth/oauth/auth_query.rb`.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed.
# Step 1: Attacker triggers a real webhook (e.g. orders/create) from their own store,
# capturing the valid raw body + Shopify-computed HMAC header sent to the app's
# public webhook endpoint (both are visible to the attacker as the recipient's traffic
# passes through infrastructure the attacker controls, e.g. a proxy or their own ngrok/log).

raw_body = '{"id": 1, "note": "malicious payload chosen by attacker"}'
valid_hmac = "<hmac header value captured from Shopify's real webhook call to attacker's own shop>"

# Step 2: Attacker replays this exact body + hmac to the app's shared public webhook
# endpoint, but swaps the shop header to target a victim shop.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # NOT covered by HMAC
  "x-shopify-api-version" => "2024-01",
  "x-shopify-webhook-id" => "attacker-chosen-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# Step 3: Registry.process validates only the body's HMAC (which is valid, since
# body/hmac pair is an untouched, legitimately-issued pair) and dispatches the
# handler believing this came from "victim-shop.myshopify.com".
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
