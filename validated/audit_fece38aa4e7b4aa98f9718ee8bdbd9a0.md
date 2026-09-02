### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) header fields are trusted by `Webhooks::Registry.process` without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content as only the raw HTTP body [1](#0-0) , while the `shop`, `topic`, `webhook_id`, and `api_version` fields are read directly from HTTP headers that are never part of the HMAC-verified data [2](#0-1) . `Webhooks::Registry.process` validates only the body's HMAC and then unconditionally forwards the unauthenticated `request.shop` value to the caller's handler as the authoritative tenant identifier [3](#0-2) .

### Finding Description
This mirrors the M-03 bug class: a field that is *acted on* (`shop`, used as the tenant/session key) is not covered by the cryptographic check that is presented as proving authenticity (the HMAC). The identity binding that should hold is:

`shop used to authorize/attribute the webhook == shop that was part of the HMAC-signed payload`

Here, `to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the digest solely over that signable string [4](#0-3) . Meanwhile `shop`, `topic`, `webhook_id` and `api_version` are pulled straight from headers [5](#0-4)  and passed downstream as trusted metadata once `Utils::HmacValidator.validate(request)` passes [6](#0-5) . Consequently, anyone who can obtain one genuine `(body, hmac)` pair signed with the app's real `client_secret` (e.g., by installing the public app on their own store and capturing its own webhook delivery) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the signature check still succeeds — the equality above is broken because the header side was never part of the check.

### Impact Explanation
If the host application (as intended by this library's `WebhookMetadata`/`Registry` design) uses `data.shop` to select the tenant's session/access-token or to attribute/write data, an attacker can spoof another shop's identity in a webhook delivery, causing cross-tenant data confusion or the app processing state changes under the wrong tenant. This matches the "shop authenticated versus shop stored/used as identity" analog called out in the rules.

### Likelihood Explanation
Requires only the ability to obtain one legitimate webhook delivery for a shop the attacker controls (a normal, unprivileged action available to anyone who can install a public Shopify app on their own store) plus the ability to send an HTTP request with attacker-chosen headers to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, document clearly that `request.shop` and other header-derived fields are unauthenticated so host applications do not use them as an identity/tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the resulting HTTP request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` computed over `B` with the app's real secret.
2. Attacker replays this exact request to the app's webhook endpoint, keeping `B` and `H` unchanged but rewriting `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(secret, B)` and compares it to `H` — this still matches, since only `B` was verified [1](#0-0) [4](#0-3) .
4. `Registry.process` accepts the request and dispatches `WebhookMetadata.new(shop: request.shop, ...)` with `shop == "victim.myshopify.com"` [7](#0-6) , causing the app to process attacker-controlled body content as if it were sent by `victim.myshopify.com`.

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
