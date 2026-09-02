## Finding

The webhook processing pipeline in `ShopifyAPI::Webhooks` validates the HMAC over only the raw request body, while the `shop-domain` header — the field used to determine tenant identity — is never covered by that signature. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop-domain header is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` accepts any request whose HMAC over the raw body validates against the app's shared `api_secret_key`. It then blindly trusts `request.shop` (read from the unsigned `X-Shopify-Shop-Domain`/`shopify-shop-domain` header) and forwards it to the app's handler as the tenant identity. Because the same `api_secret_key` is shared across every shop that installs a multi-tenant app, an attacker who installs the app on their own store receives legitimately-signed webhooks (valid `body` + `hmac` pairs). They can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. The HMAC check still passes (it only checks the body), so the forged request is accepted and dispatched to the handler with `shop` set to the victim's domain.

### Finding Description
The binding that should hold is:
`hmac_verified(body, secret) == identity_bound(shop_used_by_handler)`

In this gem that equality is broken:
- `HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string`, and for `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [2](#0-1) .
- `request.shop` is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or its HMAC [4](#0-3) .
- `Registry.process` validates the HMAC, then immediately builds `WebhookMetadata` using `request.shop` — the unverified header value — and passes it to the app's `handler.handle` [3](#0-2) .

Since `api_secret_key` is the single shared secret for the whole app (not per-shop), any attacker capable of installing the app on a shop they control can obtain a stream of validly-HMAC'd `(body, hmac)` pairs. Replaying one of those pairs against the app's public webhook endpoint with an arbitrary `shop-domain` header produces a request that passes `Utils::HmacValidator.validate` yet is attributed to any shop of the attacker's choosing — including shops they do not control.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook consumers: an unprivileged attacker (merely an app installer) can inject data that the host application will treat as originating from a different, victim shop. Depending on how the host application's webhook handler uses `shop` (e.g., to look up/update per-shop state, sync data, or trigger side effects), this enables cross-tenant data injection/corruption without needing the victim's credentials, access token, or any interception — satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Any user can freely install the target app on their own development/test shop, which is a normal, unprivileged action; from there they can capture as many valid `(body, hmac)` pairs as they like and replay them with a spoofed `shop-domain` header at will, since the header is not part of the signed material.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signable material for webhooks, or otherwise cryptographically bind the reported shop domain to the signed payload before it is trusted. At minimum, `Registry.process` should cross-check the header-provided shop against an authoritative source (e.g., verify the `webhook_id` was actually registered for that shop) rather than propagating an unauthenticated header value as tenant identity.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, receiving genuine webhooks (e.g., `orders/create`) HMAC'd with the app's shared `api_secret_key`.
2. Attacker captures one such webhook's raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed as `HMAC-SHA256(secret, B)`, per `Request#to_signable_string`/`HmacValidator`) [5](#0-4) .
3. Attacker sends a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [6](#0-5) .
5. The handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop [7](#0-6) .

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
