## Title
Webhook `shop` (and `topic`) identity is trusted by `ShopifyAPI::Webhooks::Registry.process` without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop` (and `topic`) values that are handed to the app's handler as authoritative tenant-identifying metadata come from HTTP headers that are **not** included in the signed payload. Because a single app-level `api_secret_key` is shared across every shop that has installed the app, any merchant (including an attacker who legitimately installs the app on their own free/dev store) can obtain a validly-HMAC-signed webhook body for their own store, then replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header claiming to be a different, victim shop. The HMAC still validates because it never covered the header, letting the attacker inject data/events attributed to another tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`hmac` is read from the `hmac-sha256` header, but `shop` is read from the separate `shop-domain` header, and `to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and the app's `api_secret_key`: [3](#0-2) 

`Registry.process` uses this HMAC check as the sole authentication gate, then immediately trusts `request.shop` (and `request.topic`) — values that were never part of the signed bytes — to build the metadata handed to the app's business-logic handler: [4](#0-3) 

The equality the gem implicitly promises but breaks is://
`shop bound by HMAC(api_secret_key, signed_bytes)` == `shop delivered in WebhookMetadata to the handler`

In reality the signed bytes are only the JSON body; `shop` is carried in an independent, unauthenticated header. Since Shopify signs webhooks for *all* shops of a given app with the *same* `api_secret_key`, an attacker who is a legitimate merchant of the app (an "unprivileged internet user" with no special access) can:
1. Install the target app on their own store and receive a real webhook (e.g. `orders/create`) with a genuinely valid `X-Shopify-Hmac-Sha256` for its body.
2. Replay that exact body to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` (and, if desired, `X-Shopify-Topic`) header with a victim shop's domain.
3. `Utils::HmacValidator.validate` still returns `true` (body+secret match), and `Registry.process` dispatches the event to the app's handler tagged as originating from the victim shop.

### Impact Explanation
This breaks the tenant isolation the gem is expected to provide via webhook HMAC verification, letting one merchant's app-installation inject spoofed events (data or lifecycle webhooks such as `app/uninstalled`, `orders/*`, `customers/data_request`, etc.) attributed to a different merchant. Depending on what the host app does with `WebhookMetadata#shop` (commonly: look up the stored session/access token for that shop and act on it, or trigger data mutation/GDPR-style flows for that shop), this results in cross-tenant access/data corruption — a Critical-severity outcome per the specified impact criteria.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even free-tier) installer of the target Shopify app — no access to `api_secret_key`, access tokens, or privileged accounts is needed. Capturing one's own valid webhook body/HMAC and replaying it with a modified header is trivial HTTP tooling, making this readily reachable by any unprivileged internet user who installs the app.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material the gem verifies, or otherwise cryptographically bind them to the body before trusting `request.shop` in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that consuming applications must independently corroborate the shop header against their own installed-shop records (e.g., verifying an active session exists for that shop) rather than trusting the webhook-supplied shop as authenticated by the HMAC.

### Proof of Concept
1. As Shop A (attacker-controlled, legitimately installed app), trigger any webhook, e.g. `orders/create`, and capture:
   - Body `B`
   - Header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` with the app's shared `api_secret_key`)
2. Send a new HTTP POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic: orders/create`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`.
4. `handler.handle` is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the app to process attacker-supplied order data as if it belongs to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
