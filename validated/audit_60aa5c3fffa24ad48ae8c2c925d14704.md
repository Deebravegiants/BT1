### Title
Webhook Shop-Domain Header Is Not Covered by HMAC, Allowing Cross-Tenant Webhook Forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC that `ShopifyAPI::Webhooks::Registry.process` validates covers body integrity only. The `shop` value the gem extracts (from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header) and hands to every app's webhook handler as the tenant identifier is never part of the signed bytes, breaking the equality "shop trusted by the handler == shop bound by the signature."

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`to_signable_string` returns `@raw_body` only — none of the Shopify headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) are included. `Registry.process` validates the HMAC and then builds `WebhookMetadata` straight from the unverified header-derived `shop` field: [2](#0-1) 

`WebhookMetadata.shop` is the field host applications are documented to rely on as the tenant identifier for the webhook: [3](#0-2) 

Because `Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the raw body) against the HMAC computed with the app's single `api_secret_key`/`client_secret` (shared across every shop that installs the app), any request with a body+HMAC pair that is valid for *some* shop passes validation regardless of which `shop-domain` header value is attached: [4](#0-3) 

Equality that should hold but doesn't: `shop_bound_by_hmac == shop_delivered_to_handler`. Before the attack: Shopify sends body `B`, `hmac = HMAC(secret, B)`, and header `shop-domain = shopA` — all three are self-consistent because Shopify itself only ever sends this triple together. After the attacker's request: body `B` and `hmac = HMAC(secret, B)` remain identical (still valid), but `shop-domain` is swapped to `shopB`. `HmacValidator.validate` still returns `true` because it never inspects `shop-domain`, so `Registry.process` calls the handler with `WebhookMetadata(shop: "shopB", body: B, ...)` even though the payload never originated from `shopB`.

### Impact Explanation
This is Critical — cross-tenant access. An unprivileged attacker who has installed the app on their own shop (`shopA`) receives genuine, validly-signed webhooks addressed to their own callback URL. They can capture one such delivery (body + `X-Shopify-Hmac-Sha256`) and replay it to the same endpoint with only the `X-Shopify-Shop-Domain` header changed to a victim shop (`shopB`) that also has the app installed. Because the header is outside the signed bytes, the forged request still passes `HmacValidator.validate`, and the host application's webhook handler processes attacker-controlled data as if it came from `shopB`. Depending on how the host app consumes `data.shop` (e.g., to look up the shop's session/access token, or to write/update records keyed by shop), this can inject or corrupt another tenant's data, or trigger shop-scoped actions using the attacker's payload under the victim's identity — a cross-tenant boundary break entirely enabled by this gem's request-verification design.

### Likelihood Explanation
High. No secret, access token, or privileged account is required beyond installing the app on an attacker-owned shop (which is the normal, unprivileged onboarding flow for any Shopify app). Capturing and replaying an HTTP request with one header field changed is trivial, and the gem's own `Request` parsing explicitly treats `shop-domain` as ordinary header metadata, never asserting it is part of the signed payload.

### Recommendation
Include the shop domain (and ideally webhook id/topic) in the HMAC-signed content, or otherwise cryptographically bind the shop identity to the payload before trusting it. At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header value so that any tampering with it invalidates the HMAC, restoring the equality between the shop verified by the signature and the shop delivered to `WebhookHandler#handle`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and stands up a callback endpoint that logs raw requests instead of (or in addition to) forwarding them to the app.
2. Shopify delivers a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker resends the exact same body `B` and `X-Shopify-Hmac-Sha256` value to the target app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. The app calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers))`.
5. `Utils::HmacValidator.validate(request)` returns `true` (HMAC only covers `B`), and the registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` — attacker-controlled data attributed to a shop the attacker does not own.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
